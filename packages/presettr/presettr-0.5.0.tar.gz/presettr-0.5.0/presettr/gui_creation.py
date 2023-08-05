# encoding: utf-8

import collections

import guidata.dataset.dataitems as di
import guidata.dataset.datatypes as dt

from . import _context_stack
from .base import ParameterSet


def begin_group(dct, name, is_expert_group, use_tabs):
    if is_expert_group:
        is_expert_value = dt.ValueProp(False)
        expert_checkbox = di.BoolItem(label="enable expert settings")
        expert_checkbox = expert_checkbox.set_prop("display", store=is_expert_value)
        expert_checkbox._name = "is_expert"
        dct["is_expert_%s" % name] = expert_checkbox
    if use_tabs:
        item = dt.BeginTabGroup(name)
    else:
        item = dt.BeginGroup(name)
    item._name = name
    if is_expert_group:
        item = item.set_prop("display", active=is_expert_value)
    dct["bg_%s" % name] = item


def end_group(dct, name, use_tabs):
    item = dt.EndTabGroup(name) if use_tabs else dt.EndGroup(name)
    item._name = name
    dct["eg_%s" % name] = item


def build_guidata_items(parameter_set, dct, use_tabs=False):
    """
    g is item.group_stack, "bg" means "begin group", "eg" is "end group",
    how gui items are created:

        item(g=())  render_item
        item(g=(1)) bg_1
                    render_item
        item(g=(2)) eg_1
                    bg_2
                    render_item

        item(g=(2, 3)) bg_3
                    render_item

        item(g=(2)) eg_3
                    render_item

        item(g=(2, 4, 5)) bg_4
                        bg_5
                        render_item

        item(g=(2)) eg_5
                    eg_4
                    render_item
        eg_2
    """

    current_stack = []
    for item_name, item in parameter_set._items.items():
        if isinstance(item, ParameterSet):
            continue

        if item._group_stack != tuple(current_stack):
            while len(current_stack) and len(item._group_stack) <= len(current_stack):
                # POP = close groups
                tmp_name = current_stack.pop()
                end_group(dct, tmp_name, use_tabs)
            while len(item._group_stack) > len(current_stack):
                # PUSH = open groups
                tmp_name = item._group_stack[len(current_stack)]
                current_stack.append(tmp_name)
                key = tuple(current_stack)
                is_expert_group = key in _context_stack.current_context().expert_groups
                begin_group(dct, tmp_name, is_expert_group, use_tabs)
        gui_item = item.setup_gui_item()
        gui_item._name = ""
        dct[item_name] = gui_item

    # POP = close groups until stack is empty
    while len(current_stack):
        close = current_stack[-1]
        del current_stack[-1]
        end_group(dct, close, use_tabs)


def create_widget(parameter_set, use_tabs):
    dct = collections.OrderedDict()
    build_guidata_items(parameter_set, dct, use_tabs)
    clz = type("DataSet_%s" % parameter_set.__class__.__name__, (dt.DataSet,), dct)
    clz.__doc__ = parameter_set.__doc__
    return clz


def linearize(parameter_set):

    def _linearize(parameter_set, li):
        li.append(parameter_set)
        for name, item in parameter_set._items.items():
            if isinstance(item, ParameterSet):
                _linearize(item, li)

    li = []
    _linearize(parameter_set, li)
    return li


"""
todo:
  + checks !
  + propagate change
  + title, helpstring, docstring
  + andere items

  - cleanup
  - tests

  - presets
    -> Dialog patchen oder combo box mit callback erzeugen welcher "alles macht" =
  + i/o : via pickle
"""


def create_dlg(c, use_tabs=False):

    dlgs = []

    # checked_propagation: erst nach dem edit fertig ist propagations bestimmen
    # und dialog mit "uebernehmen button" anbieten

    for i, ci in enumerate(linearize(c)):
        dlg = create_widget(ci, use_tabs)(ci._name or "")
        dlgs.append(dlg)
    g = dt.DataSetGroup(dlgs, title='Parameters group')
    return g
