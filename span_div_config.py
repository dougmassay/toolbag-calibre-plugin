# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

import os
import math

try:
    from qt.core import (Qt, QLabel, QLineEdit, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialogButtonBox)
except ImportError:
    try:
        from PyQt5.Qt import (Qt, QLabel, QLineEdit, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialogButtonBox)
    except ImportError:
        from PyQt4.Qt import (Qt, QLabel, QLineEdit, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialogButtonBox)

from calibre.utils.config import JSONConfig
from calibre.gui2 import question_dialog

from calibre.gui2.tweak_book.widgets import Dialog
from calibre_plugins.diaps_toolbag.__init__ import PLUGIN_SAFE_NAME
from calibre_plugins.diaps_toolbag.dialogs import TAGLIST, CHANGE_TO_MAP, ATTRS_LIST

from calibre_plugins.diaps_toolbag.utilities import is_py3

if is_py3:
    text_type = str
    binary_type = bytes
else:
    range = xrange  # noqa
    text_type = unicode  # noqa
    binary_type = str

# pulls in translation files for _() strings
try:
    load_translations()
except NameError:
    pass  # load_translations() added in calibre 1.9

# This is where all preferences for this plugin will be stored.
plugin_prefs = JSONConfig('plugins/{0}_SpanDivEdit_settings'.format(PLUGIN_SAFE_NAME))

# Set default preferences
for tag in TAGLIST:
    plugin_prefs.defaults['{}_changes'.format(tag)] = CHANGE_TO_MAP[tag]
plugin_prefs.defaults['attrs'] = ATTRS_LIST
plugin_prefs.defaults['taglist'] = TAGLIST

class ConfigWidget(Dialog):
    def __init__(self, gui):
        self.gui = gui
        self.qlinedit_widgets = {}
        self.taglist = plugin_prefs['taglist']
        Dialog.__init__(self, _('Edit Spans & Divs Customization'), '{}plugin:spandiv_config'.format(PLUGIN_SAFE_NAME), gui)

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        columns_frame = QHBoxLayout()
        layout.addLayout(columns_frame)

        # How many columns of eight items each will it take to display
        # a text box for each tag in taglist?
        col_limit = 8
        num_cols = len(self.taglist)/col_limit
        num_cols = int(math.ceil(num_cols))

        # If the column limit and the number of columns produces a single
        # orphan text entry widget, reduce the column limit accordingly.
        if num_cols > 1 and (len(self.taglist) - ((num_cols - 1)*col_limit)) < 2:
            if num_cols >= 3:
                col_limit -= 1

        # Create an integer-indexed dictionary of QVBoxLayouts representing the number of
        # columns necessary. Added left to right in the parent QHBoxLayout.
        column = {}
        for i in range(1, num_cols+1):
            column[i] = QVBoxLayout()
            column[i].setAlignment(Qt.AlignLeft)
            columns_frame.addLayout(column[i])

        # Create a dictionary of QLineEdit widgets (indexed by tag name) and stack them
        # (top to bottom) and their labels in as many columns as it takes.
        curr_col = 1
        curr_item = 1
        tooltip = _('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')
        for tag in self.taglist:
            # Column item limit surpassed - switch to next column.
            if curr_item > col_limit:
                column[curr_col].addStretch()
                curr_col += 1
                curr_item = 1
            # Add lable and QLineEdit widget to current column.
            label = QLabel(_('<b>Choices to change "{}" elements to:</b>').format(tag), self)
            label.setAlignment(Qt.AlignCenter)
            changes_str = ''
            if '{}_changes'.format(tag) in plugin_prefs:
                changes_str = ', '.join(plugin_prefs['{}_changes'.format(tag)])
            self.qlinedit_widgets[tag] = QLineEdit(changes_str, self)
            self.qlinedit_widgets[tag].setToolTip('<p>{}'.format(tooltip))
            column[curr_col].addWidget(label)
            column[curr_col].addWidget(self.qlinedit_widgets[tag])

            # if not len(plugin_prefs['{}_changes'.format(tag)]):
            #    self.qlinedit_widgets[tag].setDisabled(True)
            curr_item += 1
        column[curr_col].addStretch()

        layout.addSpacing(10)
        attrs_layout = QVBoxLayout()
        attrs_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(attrs_layout)

        labeltags = QLabel(_('<b>Tags available to search for:</b>'), self)
        labeltags.setAlignment(Qt.AlignCenter)
        self.tags_txtBox = QLineEdit(', '.join(plugin_prefs['taglist']), self)
        self.tags_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html tag names (no quotes).')))
        attrs_layout.addWidget(labeltags)
        attrs_layout.addWidget(self.tags_txtBox)

        labelattrs = QLabel(_('<b>HTML attributes available to search for:</b>'), self)
        labelattrs.setAlignment(Qt.AlignCenter)
        self.attrs_txtBox = QLineEdit(', '.join(plugin_prefs['attrs']), self)
        self.attrs_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html attribute names (no quotes).')))
        attrs_layout.addWidget(labelattrs)
        attrs_layout.addWidget(self.attrs_txtBox)

        layout.addSpacing(10)
        right_layout = QHBoxLayout()
        right_layout.setAlignment(Qt.AlignRight)
        layout.addLayout(right_layout)
        reset_button = QPushButton(_('Reset all defaults'), self)
        reset_button.setToolTip('<p>{}'.format(_('Reset all settings to original defaults.')))
        reset_button.clicked.connect(self.reset_defaults)
        right_layout.addWidget(reset_button)

        layout.addSpacing(10)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def save_settings(self):
        # Save current dialog sttings back to JSON config file
        for tag in self.taglist:
            tmp_list = text_type(self.qlinedit_widgets[tag].displayText()).split(',')
            tmp_list = [x.strip(' ') for x in tmp_list]
            plugin_prefs['{}_changes'.format(tag)] = list(filter(None, tmp_list))

        tmp_list = text_type(self.attrs_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['attrs'] = list(filter(None, tmp_list))
        tmp_list = text_type(self.tags_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['taglist']= list(filter(None, tmp_list))
        self.accept()

    def reset_defaults(self):
        caption= _('Are you sure?')
        msg = '<p>{}'.format(_('Reset all customizable options to their original defaults?'))
        det_msg = ''
        if question_dialog(self.gui, caption, msg, det_msg):
            for tag in TAGLIST:
                plugin_prefs['{}_changes'.format(tag)] = CHANGE_TO_MAP[tag]
            plugin_prefs['attrs'] = ATTRS_LIST
            plugin_prefs['taglist'] = TAGLIST
            self.accept()
