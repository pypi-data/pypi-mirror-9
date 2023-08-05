# encoding: utf-8

import guidata.py3compat
import guidata.utils

import guidata.dataset.dataitems as di
import guidata.dataset.qtitemwidgets as qtiw
import guidata.dataset.qtwidgets as qtw

from guidata.qt.QtGui import QWidget
from guidata.qt.QtCore import SIGNAL


def patch_bugs():
    """patch bugs in guidata 1.6.1 for handling of empty file/directory fields"""

    def to_text_string(obj, encoding=None, _orig_function=guidata.py3compat.to_text_string):
        if obj is None:
            return None
        return _orig_function(obj, encoding)

    guidata.py3compat.to_text_string = to_text_string

    def add_extension(item, value, _orig_function=guidata.utils.add_extension):
        if value is None:
            return None
        return _orig_function(item, value)

    guidata.utils.add_extension = add_extension

    def from_string(self, value):
        value = to_text_string(value)
        if value is None:
            return []
        if value.endswith("']"):
            value = eval(value)
        else:
            value = [value]
        return [add_extension(self, path) for path in value]

    di.FilesOpenItem.from_string = from_string


def patch_choice_widget():
    """callback now returns value aka label, not numerical index of choice"""
    class PatchedChoiceWidget(qtiw.ChoiceWidget):

        def index_changed(self, index):
            if self.store:
                self.store.set(self.item.instance, self.item.item, self.value())
                self.parent_layout.refresh_widgets()
            cb = self.item.get_prop_value("display", "callback", None)
            if cb is not None:
                if self.build_mode:
                    self.set()
                else:
                    self.parent_layout.update_dataitems()
                # the next two lines are the modified ones for pushing the choice value to the
                # callback, not its index:
                choices = self.item.get_prop_value("data", "choices")
                cb(self.item.instance, self.item.item, choices[self.value()][1])
                self.parent_layout.update_widgets(except_this_one=self)

    # this overwrites existing registration:
    qtw.DataSetEditLayout.register(di.ChoiceItem, PatchedChoiceWidget)


def patch_multiplie_choice_widget():
    """implements missing call to callback function"""

    class PatchedMultipleChoiceWidget(qtiw.MultipleChoiceWidget):

        """Adds callback call to MultipleChoiceWidget which is not implemented for this in guidata
        """

        def __init__(self, item, parent_layout):
            super(PatchedMultipleChoiceWidget, self).__init__(item, parent_layout)
            for box in self.boxes:
                QWidget.connect(box, SIGNAL("toggled(bool)"), self.choice_toggled)

        def choice_toggled(self, flag):
            flags = tuple(box.isChecked() for box in self.boxes)
            choices = self.item.get_prop_value("data", "choices")
            value = tuple(c[1] for (c, flag) in zip(choices, flags) if flag)
            cb = self.item.get_prop_value("display", "callback", None)
            if cb is not None:
                if self.build_mode:
                    self.set()
                else:
                    self.parent_layout.update_dataitems()
                cb(self.item.instance, self.item.item, value)
                self.parent_layout.update_widgets(except_this_one=self)

    # this overwrites existing registration:
    qtw.DataSetEditLayout.register(di.MultipleChoiceItem, PatchedMultipleChoiceWidget)


def patch_checkbox_widget():
    """implements missing call to callback function"""

    class PatchedCheckBoxWidget(qtiw.CheckBoxWidget):

        """Adds callback call to BoolItemWidget which is not implemented for this in guidata
        """

        def __init__(self, item, parent_layout):
            super(PatchedCheckBoxWidget, self).__init__(item, parent_layout)
            QWidget.connect(self.checkbox, SIGNAL("toggled(bool)"), self.toggled)

        def toggled(self, value):
            cb = self.item.get_prop_value("display", "callback", None)
            if cb is not None:
                if self.build_mode:
                    self.set()
                else:
                    self.parent_layout.update_dataitems()
                cb(self.item.instance, self.item.item, value)
                self.parent_layout.update_widgets(except_this_one=self)

    # this overwrites existing registration:
    qtw.DataSetEditLayout.register(di.BoolItem, PatchedCheckBoxWidget)


def apply_patches():
    patch_bugs()
    patch_choice_widget()
    patch_multiplie_choice_widget()
    patch_checkbox_widget()
