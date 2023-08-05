# Varlet

Varlet lets you prompt for variables at runtime, and saves them to a variables module.

## Install

    pip install varlet

## Usage

In your settings.py file add:

```python
from varlet import variable
```

whenever you declare a variable that could change depending on the environment,
use:

```python
# It is OK to make this True if you are in dev
DEBUG = variable("DEBUG", default=False)
```

If this "DEBUG" variable is not defined in the variables module (somewhere in
your python path), the user is prompted to enter a Python expression to set it.

When the prompt is displayed, the comments directly above the call to
`variable()` are displayed, and the prompt has a default value as specified by
the `default` argument.


## Implementation Details

varlet assumes there is a `variables` module located somewhere in your Python
path. If it is not found, it will attempt to create one based on the location
of `__main__`.

When a variable is set to a value, varlet will eval the value (to make sure it
is valid python), and then perform `ast.literal_eval(repr(value))` to ensure that the value
has a valid representation that can be written to a file. The `repr(value)` is
then appended to the end of the `variables` module (along with any comments
associated with the value).

If STDIN is not a tty-like interface, then a KeyError is raise if the variable
is not set in the variables module.
