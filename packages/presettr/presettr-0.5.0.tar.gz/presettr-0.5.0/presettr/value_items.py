import types
import os

import guidata.dataset.dataitems as di

from .base import ConfigItem


class Value(ConfigItem):

    def __init__(self, default=None, **options):
        super(Value, self).__init__(name="")
        self.value = default
        self.target = None
        self.options = options
        if default is not None:
            self._check_default(default)

    def _check_default(self, default):
        if not self.check_type(default):
            raise Exception("can not set %r to value %r because of type mismatch" % (self, value))
        if not self.check_value(default):
            raise Exception("can not set %r to value %r, value check fails" % (self, value))

    def setup_value(self, value):
        return value

    def callback(self, data_set, gui_item, value):
        value_item = gui_item.get_prop("extension", "value_item")
        value_item.value = value
        target = value_item.target
        if target is not None:
            to, method = target
            to.value = method(value)  # sets value to value_item
            setattr(data_set, to._name, method(value))  # sets value to gui_item

    def setup_gui_item(self):
        # we are changing options below, so we work with a copy
        options = self.options.copy()
        if "label" not in options:
            options["label"] = self._name
        options["default"] = self.value
        gui_item = self.create_gui_item(options)
        gui_item.set_prop("display", callback=self.callback)
        return wrap(gui_item, self)

    def __get__(self, from_, type_):
        return self.value


def wrap(gui_item, value_item):
    """set property for retreiving value_item from gui_item
       and pathc gui_items check method:
    """

    # we monkey patch the check_value method but still want to have access to the originial
    # method from guidata as it implements many features which we want to use too, eg checking for
    # a min or max value, etc...
    # binding the original method to a parameter does the trick which was not obvious, so test
    # carefully if you have a reason to change this:

    def check_value(self, value, orig_check_value=gui_item.check_value):
        value_item = self.get_prop("extension", "value_item")
        ok_value_item = hasattr(value_item, "check_value") and value_item.check_value(value)
        ok_gui_item = orig_check_value(value)
        return ok_value_item and ok_gui_item

    gui_item.set_prop("extension", value_item=value_item)
    gui_item.check_value = types.MethodType(check_value, gui_item)
    return gui_item


class NumberValue(Value):

    def check_value(self, value):
        min_ = self.options.get("min")
        max_ = self.options.get("max")
        if min_ is not None and value < min_:
            return False
        if max_ is not None and value > max_:
            return False
        return True


class IntValue(NumberValue):

    def check_type(self, value):
        return isinstance(value, int)

    def create_gui_item(self, options):
        return di.IntItem(**options)


class FloatValue(NumberValue):

    def check_type(self, value):
        return isinstance(value, (int, long, float))

    def create_gui_item(self, options):
        return di.FloatItem(**options)


class SecondsAsMinutes(FloatValue):

    """SecondsAsMinutes: internal value is in seconds, but in GUI we have minutes"""

    def create_gui_item(self, options):
        options = options.copy()
        options["default"] = self.value / 60.0
        min_ = options.get("min")
        if min_ is not None:
            options["min"] = min_ / 60.0
        max_ = options.get("max")
        if max_ is not None:
            options["max"] = max_ / 60.0

        # pass value in seconds to gui item as minutes:
        if "round_digits" in options:
            round_digits = options.pop("round_digits")
            for k in ("default", "min", "max"):
                options[k] = round(options[k], round_digits)

        item = di.FloatItem(**options)
        return item

    def callback(self, data_set, gui_item, value):
        value_item = gui_item.get_prop("extension", "value_item")
        value_item.value = value * 60.0
        target = value_item.target
        if target is not None:
            to, method = target
            to.value = method(value)  # sets value to value_item
            setattr(data_set, to._name, method(value))  # sets value to gui_item


class StringValue(Value):

    def check_type(self, value):
        return isinstance(value, basestring)

    def check_value(self, value):
        return True

    def create_gui_item(self, options):
        return di.StringItem(**options)


class IntListValue(StringValue):

    def check_type(self, value):
        print("check_type", repr(value))
        return isinstance(value, (tuple, list)) and all(isinstance(i, (int, long)) for i in value)

    def check_value(self, value):
        min_len = self.options.get("min_length", 0)
        if isinstance(value, (list, tuple)):
            return len(value) >= min_len and all(isinstance(i, (int, long)) for i in value)
        assert isinstance(value, basestring)
        values = [v.strip() for v in value.split(",")]
        try:
            map(int, values)
        except:
            return False
        else:
            return len(values) >= min_len

    def create_gui_item(self, options):
        options = options.copy()
        if "min_length" in options:
            del options["min_length"]
        options["default"] = ", ".join(map(str, self.value))
        item = di.StringItem(**options)
        return item

    def callback(self, data_set, gui_item, value):
        value_item = gui_item.get_prop("extension", "value_item")
        fields = [v.strip() for v in value.split(",")]
        value_item.value = map(int, fields)
        target = value_item.target
        if target is not None:
            to, method = target
            to.value = method(value)  # sets value to value_item
            setattr(data_set, to._name, method(value))  # sets value to gui_item


class BoolValue(Value):

    def check_type(self, value):
        return isinstance(value, bool)

    def check_value(self, value):
        return True

    def create_gui_item(self, options):
        return di.BoolItem(**options)


class _FiniteDomainValue(Value):

    def __init__(self, choices, *a, **kw):
        # order matters as Value.__init__ introduces check which needs choices attributes
        self.choices = choices
        super(_FiniteDomainValue, self).__init__(*a, **kw)

    def check_type(self, value):
        return True

    def check_value(self, value):
        return value in self.choices


class SingleValued(_FiniteDomainValue):

    def create_gui_item(self, options):
        if not all(isinstance(c, basestring) for c in self.choices):
            raise Exception("MultipleValued only works with strings as choices")
        options = options.copy()
        options["choices"] = self.choices
        if self.value is not None:
            options["default"] = self.choices.index(self.value)
        return di.ChoiceItem(**options)

    def _setup_value(self, value):
        if isinstance(value, int):
            # if value is int and all choices are not int: choose by index:
            if any(isinstance(c, int) for c in self.choices):
                return value
            try:
                new_value = self.choices[value]
            except IndexError:
                raise IndexError("index %d is out of range for %r" % (value, self))
            return new_value
        return super(SingleValued, self).setup_value(value)


class MultipleValued(_FiniteDomainValue):

    def create_gui_item(self, options):
        if not all(isinstance(c, basestring) for c in self.choices):
            raise Exception("MultipleValued only works with strings as choices")
        options = options.copy()
        options["choices"] = self.choices
        cols = options.get("cols")
        rows = options.get("rows")
        if cols:
            del options["cols"]
        if rows:
            del options["rows"]
        if self.value is not None:
            options["default"] = [i for (i, v) in enumerate(self.choices) if v in self.value]
        gui_item = di.MultipleChoiceItem(**options)
        if cols:
            gui_item = gui_item.vertical(cols)
        if rows:
            gui_item = gui_item.horizontal(rows)
        return gui_item

    def _setup_value(self, value):
        if all(isinstance(v, int) for v in value):
            # if value is int and all choices are not int: choose by index:
            if any(isinstance(c, int) for c in self.choices):
                return value
            new_values = []
            try:
                for v in value:
                    new_value = self.choices[v]
                    new_values.append(new_value)
            except IndexError:
                raise IndexError("index %d is out of range for %r" % (value, self))
            return new_values
        return super(MultipleValued, self).setup_value(value)

    def check_type(self, value):
        return True

    def check_value(self, value):
        return all(vi in self.choices for vi in value)


class ExistingFileValue(StringValue):

    def check_type(self, value):
        return isinstance(value, basestring)

    def check_value(self, value):
        return os.path.exists(value)

    def create_gui_item(self, options):
        return di.FileOpenItem(**options)


class ExistingFilesValue(StringValue):

    def check_type(self, value):
        return isinstance(value, (tuple, list)) and all(isinstance(v, basestring) for v in value)

    def check_value(self, value):
        return all(os.path.exists(v) for v in value)

    def create_gui_item(self, options):
        options = options.copy()
        options["default"] = options.get("default") or [""]
        return di.FilesOpenItem(**options)


class FileForSaveValue(StringValue):

    def check_type(self, value):
        return isinstance(value, basestring)

    def check_value(self, value):
        dirname = os.path.dirname(value)
        return os.path.exists(dirname) and os.path.isdir(dirname)

    def create_gui_item(self, options):
        options = options.copy()
        options["default"] = options.get("default") or ""
        return di.FileSaveItem(**options)


class DirectoryValue(StringValue):

    def create_gui_item(self, options):
        options = options.copy()
        options["default"] = options.get("default") or ""
        return di.DirectoryItem(**options)
