import json
from collections import OrderedDict


class ParameterSetMeta(type):

    def __new__(mcs, cls_name, base_classes, dct):
        for base in base_classes:
            if hasattr(base, "__metaclass__") and base.__metaclass__ == ParameterSetMeta:
                items = []
                for (name, attr) in dct.items():
                    if isinstance(attr, ConfigItem):
                        attr._name = name
                        items.append(attr)
                items.sort(key=lambda item: item._order)
                dct["_items"] = OrderedDict((item._name, item) for item in items)
                title = dct.get("title", "NO TITLE GIVEN")
                details = dct.get("details")
                if details:
                    dct["__doc__"] = title + "\n" + details
                else:
                    dct["__doc__"] = title

        return type.__new__(mcs, cls_name, base_classes, dct)

    def __init__(clz, name, base_classes, dct):
        clz._checks = {}
        for (name, attr) in dct.items():
            if name.startswith("check_"):
                field = name.lstrip("check_")
                if field not in dct:
                    raise Exception("field for checker %s unknwon" % name)
                # getattr(clz, field).check = lambda value, attr=attr: attr(value)
                clz._checks[field] = lambda value, attr=attr: attr(value)
        super(ParameterSetMeta, clz).__init__(name, base_classes, dct)


class ConfigItem(object):

    def __init__(self, name=None):
        from . import _context_stack
        ctx = _context_stack.current_context()
        self._order = ctx.new_order()
        self._name = name
        # stack as tuple: no chance to get into trouble with references to
        # ConfigItem.current_group_stack:
        self._group_stack = tuple(ctx.current_group_stack)


class ParameterSet(ConfigItem):
    __metaclass__ = ParameterSetMeta

    def __init__(self, name=None, expert_settings=False):
        if name is None:
            name = self.__class__.__name__
        super(ParameterSet, self).__init__(name=name)
        self._expert_settings = expert_settings

    def print_(self, indent=0):
        for item in self._items.values():
            if isinstance(item, ParameterSet):
                txt = "{}: {}".format(item._name, item.__class__.__name__)
                print " " * (indent - 1), txt
                item.print_(indent + 4)
            else:
                txt = "{}: {} = {!r}".format(item._name, item.__class__.__name__, item.value)
                print " " * (indent - 1), txt

    def check(self, name, value, item):
        ok = False
        result = item.check_type(value)
        if isinstance(result, (int, long,  bool)):
            ok = result
        else:
            raise RuntimeError("%r must return bool value" % item.check)
        if not ok:
            raise ValueError("can not set %s to %r because type check fails" % (name, value))

        ok = False
        result = item.check_value(value)
        if isinstance(result, (int, long,  bool)):
            ok = result
        else:
            raise RuntimeError("%r must return bool value" % item.check)
        if not ok:
            raise ValueError("can not set %s to %r because value check fails" % (name, value))

    def __iter__(self):
        dct = {}
        for name, item in self._items.items():
            if isinstance(item, ParameterSet):
                yield name, dict(item)
            else:
                yield name, item.value

    def __str__(self):
        shift = "    "

        def collect(obj, lines, indent="", shift=shift):
            for item in obj._items.values():
                if isinstance(item, ParameterSet):
                    lines.append(indent + "%s: {" % item._name)
                    collect(item, lines, indent + shift)
                    lines.append(indent + "}")
                else:
                    lines.append(indent + "%s = %s" % (item._name, item.value))
        lines = []
        lines.append("{")
        collect(self, lines, indent=shift)
        lines.append("}")
        return "\n".join(lines)

    def __setattr__(self, name, value):
        item = self._items.get(name)

        # recurse for nested parameter set:
        if isinstance(value, ParameterSet):
            for sub_name, sub_value in value:
                setattr(item, sub_name, sub_value)
            return

        item = self._items.get(name)
        if isinstance(self, ParameterSet) and not name.startswith("_") and item is None:
            raise Exception("value %s not known" % name)

        if item is not None and value is not None:
            # value = item.setup_value(value)
            if item.target is not None:
                to, method = item.target
                to.value = method(value)
            item.value = value
            return
        ConfigItem.__setattr__(self, name, value)

    def update(self, other):
        for name, item in other._items.items():
            if isinstance(item, ParameterSet):
                getattr(self, name).update(item)
            else:
                setattr(self, name, item.value)

    def update_from_dict(self, dd):
        """ maybe partial update if dd does not contain all value/parameter set items we defined """
        for name, item in self._items.items():
            if isinstance(item, ParameterSet):
                item.update_from_dict(dd.get(name, {}))
            else:
                old_value = getattr(self, name)
                setattr(self, name, dd.get(name, old_value))

    def overwrite_from_dict(self, dd):
        """ full update, dd must conatin al value/parameter set items we defined """
        for name, item in self._items.items():
            if name not in dd:
                raise Exception("dd misses key %r" % name)
            if isinstance(item, ParameterSet):
                item.overwrite_from_dict(dd[name])
            else:
                setattr(self, name, dd[name])

    def as_dict(self):
        return dict(self)   # uses self.__iter__

    def __getitem__(self, name):
        return getattr(self, name)

    def __getstate__(self):
        return (self.__dict__, self.as_dict())

    def __setstate__(self, (dd, values)):
        self.__dict__ = dd
        self.overwrite_from_dict(values)

    def dumps(self):
        return json.dumps(self.as_dict(), indent=4)   # indent for pretty printing

    def dump_json(self, path):
        with open(path, "w") as fp:
            fp.write(self.dumps())

    def update_from_json(self, str_):
        self.overwrite_from_dict(json.loads(str_))

    def update_from_json_file(self, path):
        with open(path, "rU") as fp:
            return self.update_from_json(fp.read())

    @classmethod
    def loads(clz, str_):
        obj = clz()
        obj.update_from_json(str_)
        return obj

    @classmethod
    def load_json(clz, path):
        obj = clz()
        obj.update_from_json_file(path)
        return obj

    def as_widget(self, use_tabs=False):
        from .gui_creation import create_widget
        return create_widget(self, use_tabs)

    def edit(self, use_tabs=False):
        from guidata import qapplication
        app = qapplication()
        from .gui_creation import create_dlg
        backup = self.as_dict()
        flag = create_dlg(self, use_tabs).edit()
        if flag == 0:  # abort self might be edited, so we use backup for restore
            self.overwrite_from_dict(backup)
        return flag
