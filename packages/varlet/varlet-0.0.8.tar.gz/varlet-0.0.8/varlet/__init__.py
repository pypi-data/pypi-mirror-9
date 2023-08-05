"""
Import variable into your Django settings.py file, and whenever you define a
variable that could change depending on where the project is deployed, use
something like:

    DEBUG = variable("DEBUG")
    DEBUG = variable("DEBUG", default=False)

Here is a more useful example:

    import os

    # This needs to be a cryptographically secure random string. The default is
    # fine.
    SECRET_KEY = variable("SECRET_KET", os.urandom(64).decode("latin1"))

When your settings file is interpreted, a call to variable will look in a
variables module (which must be in your python path somewhere) to find the value
of the setting. If it is not defined, you are prompted to enter a valid Python
expression to set it, which is then written to the variables.py file in the
location of __main__
"""
from __future__ import print_function
import os
import sys
import ast
import inspect
import tokenize
import token
import readline
import importlib
from functools import partial
from collections import defaultdict
import logging
# these are imported so I can use mock easily to patch them. Also note that I
# alias raw_input to input for Python2
try:
    from builtins import input, print
except ImportError:
    from __builtin__ import raw_input as input, print

# try to get reload in Py3 to Py3.3
try:
    from imp import reload
except ImportError:
    pass

# try to get reload in Py 3.4
try:
    from importlib import reload
except ImportError:
    pass

logger = logging.getLogger(__name__)

class AnsiFormatCode:
    BLACK = 90
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    MAGENTA = 95 # purple
    CYAN = 96 # blue/green
    WHITE = 97


def ansi_format(format_code, string, *args, **kwargs):
    """
    Returns a string wrapped in the necessary boilerplate for rendering text with an ANSI format_code

    http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
    http://stackoverflow.com/questions/9468435/look-how-to-fix-column-calculation-in-python-readline-if-use-color-prompt
    """
    return "".join(['\001\033[', str(format_code), 'm\002', string.format(*args, **kwargs), "\001\033[0m\002"])

# create a few semantically named aliases for ansi_format. Matches twitter bootstrap naming.
success = partial(ansi_format, AnsiFormatCode.GREEN)
warning = partial(ansi_format, AnsiFormatCode.YELLOW)
info = partial(ansi_format, AnsiFormatCode.BLUE)
danger = partial(ansi_format, AnsiFormatCode.RED)

# to detect if a default value is specified, we check to see if it is not this
# object using the identity operator
A_UNIQUE_VALUE = float("nan")

# the name of the module in the python path that we should load variables from
VARIABLES_MODULE = "variables"

def load_variables():
    """
    Returns a 2-tuple where the first element is a dict of variables defined in
    the variables module, and the second element is the path (or expected path) to
    the module
    """
    try:
        variables = importlib.import_module(VARIABLES_MODULE)
        # reload the module to see if anything was changed since we originally
        # loaded it. For some reason, Python caches the module and doesn't
        # reload it automatically when it changes
        reload(variables)
        # the path to the VARIABLES_MODULE. We remove the trailing c for pyc files
        variables_path = os.path.abspath(os.path.join(variables.__file__)).rstrip("c")
        variables = dict((k, v) for k, v in variables.__dict__.items() if not k.startswith("__"))
    except (OSError, ImportError) as e:
        variables = {}
        # the variables module doesn't exist in the PYTHONPATH, so we will create
        # it in the same location as __main__
        variables_path = os.path.abspath(os.path.join(os.path.dirname(getattr(sys.modules["__main__"], '__file__', '')), VARIABLES_MODULE + ".py"))
        # the default location isn't in sys.path, so error out
        if os.path.dirname(variables_path) not in sys.path:
            raise RuntimeError("You need to create a %s.py file somewhere in your PYTHONPATH!" % (VARIABLES_MODULE))

        logging.info("A %s.py file will be created in %s after you set a variable" % (VARIABLES_MODULE, variables_path))

    return variables, variables_path


def variable(name, default=A_UNIQUE_VALUE):
    variables, variables_path = load_variables()
    # if the name of the variable is not defined, we need to prompt the user for it
    if name not in variables:
        has_default = default is not A_UNIQUE_VALUE

        comment = get_preceeding_comments()
        if comment:
            print(info(comment))

        if has_default:
            # write the default to stdin when input is promoted for
            readline.set_startup_hook(lambda: readline.insert_text(repr(default)))

        while name not in variables:
            # make sure we are at a tty device
            if not os.isatty(sys.stdin.fileno()):
                raise KeyError("You need to set the variable '%s' in %s (or somewhere else in your python path)." % (name, variables_path))

            val = input(warning(name) + " = ")
            # clear the startup hook since we only want to show the default
            # value once
            readline.set_startup_hook()

            if has_default and val == "":
                val = default
            else:
                try:
                    val = eval(val)
                except Exception as e:
                    print(danger(str(e)))
                    continue

            # we need to ensure the repr of the value is valid Python
            try:
                ast.literal_eval(repr(val))
            except Exception as e:
                print(danger("The value must have a repr that is valid Python (like a number, list, dict, or string)!"))
                continue

            # everything is good, so we can actually save the value
            variables[name] = val

        # append the variable to the variables.py file
        with open(variables_path, "a+") as f:
            # write a newline if we're not at the beginning of the file, and
            # the previous line didn't end with \n
            write_new_line = f.tell() != 0 and not f.read().endswith("\n")
            if write_new_line:
                f.write("\n")
            f.write("%s" % comment + "\n" if comment else "")
            f.write("%s = %s\n" % (name, repr(val)))

    return variables[name]


# we tokenize every file that imports variable and create a dict of dicts
# where the first key is the filename, and the second key is the line number of
# a comment in that file, and the value is the actual comment line
comments = defaultdict(dict)

def get_preceeding_comments():
    global comments
    # the variable call is back 2 places on the stack
    frame = inspect.stack()[2]
    # we want to find the comment line(s) that were written directly above the
    # call to variable. We figure out what file made the call, and tokenize
    # it
    filename = frame[1]
    line_no = frame[2]
    # the first time we come across this file, we need to tokenize it to find all the comments
    if filename not in comments:
        with open(filename) as f:
            for token_type, token_string, (srow, scol), (erow, ecol), line in tokenize.generate_tokens(f.readline):
                if token.tok_name[token_type] == "COMMENT":
                    comments[filename][srow] = token_string

    # create the doc for this variable by slurping up all the consecutive
    # comment lines that occur before the calling line in the calling file
    comment = []
    comments_in_this_file = comments[filename]
    # move up to the previous line
    line_no -= 1
    while comments_in_this_file.get(line_no, None) != None:
        comment.append(comments_in_this_file[line_no])
        line_no -= 1
    # we need to reverse the list of comment lines before joining, since the
    # lines were read from bottom to top
    comment = "\n".join(reversed(comment))

    return comment
