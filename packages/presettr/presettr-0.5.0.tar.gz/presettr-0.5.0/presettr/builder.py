import contextlib


@contextlib.contextmanager
def ParameterSetBuilder():
    from . import _context_stack

    from .value_items import (IntValue, FloatValue, BoolValue, StringValue, SingleValued,
                              MultipleValued, ExistingFileValue, ExistingFilesValue,
                              FileForSaveValue, DirectoryValue, SecondsAsMinutes,
                              IntListValue)

    from .base import ParameterSet
    from .decl_helpers import propagate_change, ValueGroup

    # create and install new module global context
    _context_stack.install_new_context()

    # import classes and functions
    to_install = (IntValue, FloatValue, BoolValue, StringValue, SingleValued, MultipleValued,
                  ExistingFileValue, ExistingFilesValue, FileForSaveValue, DirectoryValue,
                  ParameterSet, ValueGroup, propagate_change, ValueGroup, SecondsAsMinutes,
                  IntListValue)

    already_there = dict()
    for obj in to_install:
        name = obj.__name__
        if name in __builtins__.keys():
            # remember already global classes and functions before overriding
            already_there[name] = __builtins__.get(name)
        __builtins__[name] = obj
    yield

    # reset overriden global names
    for name, obj in already_there.items():
        __builtins__[name] = obj

    # restore global context
    _context_stack.drop_context()
