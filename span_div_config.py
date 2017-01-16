# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

import os
try:
    from PyQt5.Qt import (Qt, QLabel, QLineEdit, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialogButtonBox)
except ImportError:
    from PyQt4.Qt import (Qt, QLabel, QLineEdit, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QDialogButtonBox)

from calibre.utils.config import JSONConfig
from calibre.gui2 import question_dialog

from calibre.gui2.tweak_book.widgets import Dialog
from calibre_plugins.diaps_toolbag.__init__ import PLUGIN_SAFE_NAME

# This is where all preferences for this plugin will be stored.
plugin_prefs = JSONConfig('plugins/{0}_SpanDivEdit_settings'.format(PLUGIN_SAFE_NAME))

# Set default preferences
plugin_prefs.defaults['span_changes'] = ['em', 'strong', 'i', 'b', 'small', 'u']
plugin_prefs.defaults['div_changes'] = ['p', 'blockquote']
plugin_prefs.defaults['p_changes'] = ['div']
plugin_prefs.defaults['i_changes'] = ['em', 'span']
plugin_prefs.defaults['em_changes'] = ['i', 'span']
plugin_prefs.defaults['b_changes'] = ['strong', 'span']
plugin_prefs.defaults['strong_changes'] = ['b', 'span']
plugin_prefs.defaults['u_changes'] = ['span']
plugin_prefs.defaults['a_changes'] = []
plugin_prefs.defaults['small_changes'] = ['span']
plugin_prefs.defaults['sec_changes'] = ['div']
plugin_prefs.defaults['block_changes'] = ['div']
plugin_prefs.defaults['attrs'] = ['class', 'id', 'style', 'href']

class ConfigWidget(Dialog):
    def __init__(self, gui):
        self.gui = gui
        Dialog.__init__(self, _('Edit Spans & Divs Customization'), '{}plugin:spandiv_config'.format(PLUGIN_SAFE_NAME), gui)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        label = QLabel(_('Choices to change "span" elements to:'), self)
        self.span_txtBox = QLineEdit(', '.join(plugin_prefs['span_changes']), self)
        self.span_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.span_txtBox)

        label = QLabel(_('Choices to change "div" elements to:'), self)
        self.div_txtBox = QLineEdit(', '.join(plugin_prefs['div_changes']), self)
        self.div_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.div_txtBox)

        label = QLabel(_('Choices to change "p" elements to:'), self)
        self.p_txtBox = QLineEdit(', '.join(plugin_prefs['p_changes']), self)
        self.p_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.p_txtBox)

        label = QLabel(_('Choices to change "i" elements to:'), self)
        self.i_txtBox = QLineEdit(', '.join(plugin_prefs['i_changes']), self)
        self.i_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.i_txtBox)

        label = QLabel(_('Choices to change "em" elements to:'), self)
        self.em_txtBox = QLineEdit(', '.join(plugin_prefs['em_changes']), self)
        self.em_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.em_txtBox)        

        label = QLabel(_('Choices to change "b" elements to:'), self)
        self.b_txtBox = QLineEdit(', '.join(plugin_prefs['b_changes']), self)
        self.b_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.b_txtBox)

        label = QLabel(_('Choices to change "strong" elements to:'), self)
        self.strong_txtBox = QLineEdit(', '.join(plugin_prefs['strong_changes']), self)
        self.strong_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.strong_txtBox)

        label = QLabel(_('Choices to change "u" elements to:'), self)
        self.u_txtBox = QLineEdit(', '.join(plugin_prefs['u_changes']), self)
        self.u_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.u_txtBox)

        label = QLabel(_('Choices to change "a" elements to:'), self)
        self.a_txtBox = QLineEdit(', '.join(plugin_prefs['a_changes']), self)
        self.a_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.a_txtBox)
        self.a_txtBox.setDisabled(True)

        label = QLabel(_('Choices to change "small" elements to:'), self)
        self.small_txtBox = QLineEdit(', '.join(plugin_prefs['small_changes']), self)
        self.small_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.small_txtBox)

        label = QLabel(_('Choices to change "section" elements to:'), self)
        self.sec_txtBox = QLineEdit(', '.join(plugin_prefs['sec_changes']), self)
        self.sec_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.sec_txtBox)

        label = QLabel(_('Choices to change "blockquote" elements to:'), self)
        self.block_txtBox = QLineEdit(', '.join(plugin_prefs['block_changes']), self)
        self.block_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')))
        layout.addWidget(label)
        layout.addWidget(self.block_txtBox)

        layout.addSpacing(10)
        label = QLabel(_('Attributes to search for in html elements:'), self)
        self.attrs_txtBox = QLineEdit(', '.join(plugin_prefs['attrs']), self)
        self.attrs_txtBox.setToolTip('<p>{}'.format(_('Comma separated list of html attribute names (no quotes).')))
        layout.addWidget(label)
        layout.addWidget(self.attrs_txtBox)

        layout.addSpacing(10)
        right_layout = QHBoxLayout(self)
        right_layout.setAlignment(Qt.AlignRight)
        layout.addLayout(right_layout)
        reset_button = QPushButton(_('Reset all defaults'), self)
        reset_button.setToolTip('<p>{}'.format(_('Reset all settings to original defaults.')))
        reset_button.clicked.connect(self.reset_defaults)
        #reset_button.setAlignment(Qt.AlignRight)
        right_layout.addWidget(reset_button)

        layout.addSpacing(10)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def save_settings(self):
        # Save current dialog sttings back to JSON config file
        tmp_list = unicode(self.span_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['span_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.div_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['div_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.p_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['p_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.i_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['i_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.em_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['em_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.b_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['b_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.strong_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['strong_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.u_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['u_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.a_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['a_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.small_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['small_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.sec_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['sec_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.block_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['block_changes'] = filter(None, tmp_list)

        tmp_list = unicode(self.attrs_txtBox.displayText()).split(',')
        tmp_list = [x.strip(' ') for x in tmp_list]
        plugin_prefs['attrs'] = filter(None, tmp_list)
        self.accept()

    def reset_defaults(self):
        caption= _('Are you sure?')
        msg = '<p>{}'.format(_('Reset all customizable options to their original defaults?'))
        det_msg = ''
        if question_dialog(self.gui, caption, msg, det_msg):
            plugin_prefs['span_changes'] = ['em', 'strong', 'i', 'b', 'small', 'u']
            plugin_prefs['div_changes'] = ['p', 'blockquote']
            plugin_prefs['p_changes'] = ['div']
            plugin_prefs['i_changes'] = ['em', 'span']
            plugin_prefs['em_changes'] = ['i', 'span']
            plugin_prefs['b_changes'] = ['strong', 'span']
            plugin_prefs['strong_changes'] = ['b', 'span']
            plugin_prefs['u_changes'] = ['span']
            plugin_prefs['a_changes'] = []
            plugin_prefs['small_changes'] = ['span']
            plugin_prefs['block_changes'] = ['div']
            plugin_prefs['attrs'] = ['class', 'id', 'style', 'href']
            self.accept()
