# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

import os
from hashlib import md5
from zipfile import ZipFile

try:
    from PyQt5.Qt import (Qt, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QTextEdit, QComboBox, QApplication,
                      QSizePolicy, QGroupBox, QPushButton, QDialogButtonBox, QHBoxLayout, QTextBrowser,
                      QSpacerItem, QProgressDialog, QListWidget, QTimer, QSize, QDialog, QIcon, QUrl)
except ImportError:
    from PyQt4.Qt import (Qt, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QTextEdit, QComboBox, QApplication,
                      QSizePolicy, QGroupBox, QPushButton, QDialogButtonBox, QHBoxLayout, QTextBrowser,
                      QSpacerItem, QProgressDialog, QListWidget, QTimer, QSize, QDialog, QIcon, QUrl)

from calibre.gui2 import error_dialog, choose_files, open_url
from calibre.utils.config import config_dir

from calibre.gui2.tweak_book.widgets import Dialog
from calibre_plugins.diaps_toolbag.__init__ import (PLUGIN_NAME, PLUGIN_SAFE_NAME)

PLUGIN_PATH = os.path.join(config_dir, 'plugins', '{}.zip'.format(PLUGIN_NAME))

# To add a new tag, add it to TAGLIST and add a list of tags it can be changed to to CHANGE_TO_MAP.
TAGLIST = ['span', 'div', 'p', 'i', 'em', 'b', 'strong', 'u', 'small', 'a', 'blockquote', 'header',
           'section', 'footer', 'nav', 'article']

CHANGE_TO_MAP = {
    'span'       : ['em', 'strong', 'i', 'b', 'small', 'u'],
    'div'        : ['p', 'blockquote'],
    'p'          : ['div'],
    'i'          : ['em', 'span'],
    'em'         : ['i', 'span'],
    'b'          : ['strong', 'span'],
    'strong'     : ['b', 'span'],
    'u'          : ['span'],
    'small'      : ['span'],
    'a'          : [],
    'blockquote' : ['div'],
    'header'     : ['div'],
    'section'    : ['div'],
    'footer'     : ['div'],
    'nav'        : ['div'],
    'article'    : ['div'],
}

ATTRS_LIST = ['class', 'id', 'style', 'href']

# pulls in translation files for _() strings
try:
    load_translations()
except NameError:
    pass  # load_translations() added in calibre 1.9

class RemoveDialog(Dialog):
    def __init__(self, parent):
        from calibre_plugins.diaps_toolbag.span_div_config import plugin_prefs as prefs
        self.criteria = None
        self.prefs = prefs
        self.parent = parent
        self.help_file_name = '{0}_span_div_help.html'.format(PLUGIN_SAFE_NAME)
        self.taglist = TAGLIST
        Dialog.__init__(self, _('Edit Spans & Divs'), 'toolbag_spans_divs_dialog', parent)

    def setup_ui(self):
        DELETE_STR = _('Delete')
        MODIFY_STR = _('Modify')
        NO_ATTRIB_STR = _('No attributes ("naked" tag)')
        self.NO_CHANGE_STR = _('No change')

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        help_layout = QHBoxLayout()
        layout.addLayout(help_layout)
        # Add hyperlink to a help file at the right. We will replace the correct name when it is clicked.
        help_label = QLabel('<a href="http://www.foo.com/">Plugin Help</a>', self)
        help_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)
        help_label.setAlignment(Qt.AlignRight)
        help_label.linkActivated.connect(self.help_link_activated)
        help_layout.addWidget(help_label)

        action_layout = QHBoxLayout()
        layout.addLayout(action_layout)
        label = QLabel(_('Action type:'), self)
        action_layout.addWidget(label)
        self.action_combo = QComboBox()
        action_layout.addWidget(self.action_combo)
        self.action_combo.addItems([DELETE_STR, MODIFY_STR])
        self.action_combo.currentIndexChanged.connect(self.update_gui)

        tag_layout = QHBoxLayout()
        layout.addLayout(tag_layout)
        label = QLabel(_('Tag name:'), self)
        tag_layout.addWidget(label)
        self.tag_combo = QComboBox()
        tag_layout.addWidget(self.tag_combo)
        self.tag_combo.addItems(self.taglist)
        self.tag_combo.currentIndexChanged.connect(self.update_gui)

        attr_layout = QHBoxLayout()
        layout.addLayout(attr_layout)
        label = QLabel(_('Having the attribute:'), self)
        attr_layout.addWidget(label)
        self.attr_combo = QComboBox()
        attr_layout.addWidget(self.attr_combo)
        self.attr_combo.addItems(self.prefs['attrs'])
        self.attr_combo.addItem(NO_ATTRIB_STR)
        self.attr_combo.currentIndexChanged.connect(self.update_gui)

        srch_layout = QHBoxLayout()
        layout.addLayout(srch_layout)
        label = QLabel(_("Whose value is (no quotes):"), self)
        srch_layout.addWidget(label)
        self.srch_txt = QLineEdit('', self)
        srch_layout.addWidget(self.srch_txt)
        self.srch_method = QCheckBox(_('Regex'), self)
        srch_layout.addWidget(self.srch_method)

        newtag_layout = QHBoxLayout()
        layout.addLayout(newtag_layout)
        label = QLabel(_('Change tag to:'), self)
        newtag_layout.addWidget(label)
        self.newtag_combo = QComboBox()
        newtag_layout.addWidget(self.newtag_combo)

        self.newtag_combo.addItem(self.NO_CHANGE_STR)
        self.newtag_combo.addItems(self.prefs['{}_changes'.format(unicode(self.tag_combo.currentText()))])

        if self.action_combo.currentIndex() == 0:
            self.newtag_combo.setDisabled(True)

        newattr_layout = QVBoxLayout()
        layout.addLayout(newattr_layout)
        label = QLabel(_('New attribute string to insert (entire):'), self)
        newattr_layout.addWidget(label)
        self.newattr_txt = QLineEdit('', self)
        newattr_layout.addWidget(self.newattr_txt)
        self.copy_attr = QCheckBox(_('Copy existing attribute string'), self)
        self.copy_attr.stateChanged.connect(self.update_txt_box)
        newattr_layout.addWidget(self.copy_attr)
        if self.action_combo.currentIndex() == 0:
            self.copy_attr.setDisabled(True)
            self.newattr_txt.setDisabled(True)

        layout.addSpacing(10)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._ok_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def update_gui(self):
        if self.attr_combo.currentIndex() == self.attr_combo.count()-1:
            self.srch_txt.clear()
            self.srch_txt.setDisabled(True)
            self.srch_method.setChecked(False)
            self.srch_method.setDisabled(True)
        else:
            self.srch_txt.setDisabled(False)
            self.srch_method.setDisabled(False)

        self.newtag_combo.clear()
        self.newtag_combo.addItem(self.NO_CHANGE_STR)
        self.newtag_combo.addItems(self.prefs['{}_changes'.format(unicode(self.tag_combo.currentText()))])

        if self.action_combo.currentIndex() == 0:
            self.newtag_combo.setCurrentIndex(0)
            self.newtag_combo.setDisabled(True)
            self.newattr_txt.clear()
            self.newattr_txt.setDisabled(True)
            self.copy_attr.setChecked(False)
            self.copy_attr.setDisabled(True)
        else:
            self.newtag_combo.setDisabled(False)
            self.newattr_txt.setDisabled(False)
            self.copy_attr.setDisabled(False)

    def update_txt_box(self):
        if self.copy_attr.isChecked():
            self.newattr_txt.clear()
            self.newattr_txt.setDisabled(True)
        else:
            self.newattr_txt.setDisabled(False)

    def _ok_clicked(self):
        if self.action_combo.currentIndex() == 0:
            action = 'delete'
        else:
            action = 'modify'
        if self.attr_combo.currentIndex() == self.attr_combo.count()-1:
            attribute = None
        else:
            attribute = unicode(self.attr_combo.currentText())
        srch_str = unicode(self.srch_txt.displayText())
        if not len(srch_str):
            srch_str = None
        if srch_str is None and attribute is not None:
            return error_dialog(self.parent, _('Error'), '<p>{0}'.format(
                    _('Must enter a value for the attribute selected')), det_msg='', show=True)
        srch_method = 'normal'
        if self.srch_method.isChecked():
            srch_method = 'regex'
        if self.newtag_combo.currentIndex() == 0:
            newtag = None
        else:
            newtag = unicode(self.newtag_combo.currentText())
        if action == 'modify' and newtag is None and self.copy_attr.isChecked():
            return error_dialog(self.parent, _('Error'), '<p>{0}'.format(
                    _('What--exactly--would that achieve?')), det_msg='', show=True)
        new_str = unicode(self.newattr_txt.displayText())
        copy_attr = False
        if self.copy_attr.isChecked():
            copy_attr = True
        if not len(new_str):
            new_str = ''

        self.criteria = (srch_str, srch_method, unicode(self.tag_combo.currentText()), attribute, action, newtag, new_str, copy_attr)
        self.accept()

    def getCriteria(self):
        return self.criteria

    def help_link_activated(self, url):
        def get_help_file_resource():
            # Copy the HTML helpfile to the plugin directory each time the
            # link is clicked in case the helpfile is updated in newer plugins.
            file_path = os.path.join(config_dir, 'plugins', self.help_file_name)
            with open(file_path,'w') as f:
                f.write(load_resource('resources/{}'.format(self.help_file_name)))
            return file_path
        url = 'file:///' + get_help_file_resource()
        open_url(QUrl(url))


class PunctDialog(Dialog):
    def __init__(self, parent):
        self.prefs = self.prefsPrep()
        self.criteria = None
        self.parent = parent
        self.help_file_name = '{0}_smarten_help.html'.format(PLUGIN_SAFE_NAME)
        Dialog.__init__(self, _('Smarten Punctuation (the sequel)'), 'toolbag_smarter_dialog', parent)

    def setup_ui(self,):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        help_layout = QHBoxLayout()
        layout.addLayout(help_layout)
        # Add hyperlink to a help file at the right. We will replace the correct name when it is clicked.
        help_label = QLabel('<a href="http://www.foo.com/">Plugin Help</a>', self)
        help_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)
        help_label.setAlignment(Qt.AlignRight)
        help_label.linkActivated.connect(self.help_link_activated)
        help_layout.addWidget(help_label)

        self.edu_quotes = QCheckBox(_('Smarten Quotation marks'), self)
        layout.addWidget(self.edu_quotes)
        self.edu_quotes.setChecked(self.prefs['edu_quotes'])
        self.edu_quotes.stateChanged.connect(self.quotes_gui_changes)

        exceptions_group_box = QGroupBox('', self)
        layout.addWidget(exceptions_group_box)
        exceptions_group_box_layout = QVBoxLayout()
        exceptions_group_box.setLayout(exceptions_group_box_layout)
        self.use_file = QCheckBox(_('Use custom apostrophe exceptions file'), self)
        exceptions_group_box_layout.addWidget(self.use_file)
        if not self.edu_quotes.isChecked():
            self.use_file.setDisabled(True)
        else:
            self.use_file.setChecked(self.prefs['use_file'])
        self.use_file.stateChanged.connect(self.use_file_gui_changes)

        path_layout = QHBoxLayout()
        exceptions_group_box_layout.addLayout(path_layout)
        self.file_path = QLineEdit('', self)
        if not self.edu_quotes.isChecked() and not self.use_file.isChecked():
            self.file_path.setReadOnly(True)
        else:
            self.file_path.setText(self.prefs['file_path'])
            self.file_path.setReadOnly(True)
        path_layout.addWidget(self.file_path)
        self.file_button = QPushButton('...', self)
        self.file_button.clicked.connect(self.getFile)
        path_layout.addWidget(self.file_button)
        if not self.edu_quotes.isChecked() and not self.use_file.isChecked():
            self.file_button.setDisabled(True)

        combo_layout = QVBoxLayout()
        layout.addLayout(combo_layout)
        label = QLabel(_('(em|en)-dash settings'), self)
        combo_layout.addWidget(label)
        self.dashes_combo = QComboBox()
        combo_layout.addWidget(self.dashes_combo)
        values = [_('Do not educate dashes'), _('-- = emdash (no endash support)'),
                  _('-- = emdash | --- = endash'), _('--- = emdash | -- = endash')]
        self.dashes_combo.addItems(values)
        self.dashes_combo.setCurrentIndex(self.prefs['dashes'])
        # self.dashes_combo.currentIndexChanged.connect(self.update_gui)

        self.ellipses = QCheckBox(_('Smarten ellipses'), self)
        layout.addWidget(self.ellipses)
        self.ellipses.setChecked(self.prefs['ellipses'])

        self.unicode = QCheckBox(_('Educate with unicode characters (instead of entities)'), self)
        layout.addWidget(self.unicode)
        self.unicode.setChecked(self.prefs['unicode'])

        layout.addSpacing(10)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._ok_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def getFile(self):
        unique_dlg_name = '{0}plugin:smarter_choose_dialog'.format(PLUGIN_SAFE_NAME)
        caption = _('Select custom apostrophe exceptions file')
        filters = [('Text files', ['txt'])]
        c = choose_files(self, unique_dlg_name, caption, filters, all_files=True)

        if c:
            self.file_path.setReadOnly(False)
            self.file_path.setText(c[0])
            self.file_path.setReadOnly(True)

    def _ok_clicked(self):
        quotes_setting = 'q' if self.edu_quotes.isChecked() else ''
        if self.dashes_combo.currentIndex() == 0:
            dash_setting = ''
        elif self.dashes_combo.currentIndex() == 1:
            dash_setting = 'd'
        elif self.dashes_combo.currentIndex() == 2:
            dash_setting = 'i'
        elif self.dashes_combo.currentIndex() == 3:
            dash_setting = 'D'
        else:
            dash_setting = ''
        ellipses_setting = 'e' if self.ellipses.isChecked() else ''
        smarty_attr = quotes_setting + dash_setting + ellipses_setting
        if smarty_attr == '':
            smarty_attr = '0'

        self.file_path.setReadOnly(False)
        if self.use_file.isChecked() and not len(self.file_path.displayText()):
            self.file_path.setReadOnly(True)
            return error_dialog(self.parent, _('Error'), '<p>' +
                    _('Must select a custom exception file'), det_msg='', show=True)
        if self.use_file.isChecked():
            apos_exception_file = unicode(self.file_path.displayText())
            if not os.path.exists(apos_exception_file):
                apos_exception_file = None
        else:
            apos_exception_file = None
        self.file_path.setReadOnly(True)
        apos_words_list = []
        if apos_exception_file is not None:
            apos_words_list = self.parseExceptionsFile(os.path.normpath(apos_exception_file))
        self.criteria = (smarty_attr, self.unicode.isChecked(), apos_words_list)
        self.savePrefs()
        self.accept()

    def getCriteria(self):
        return self.criteria

    def quotes_gui_changes(self):
        if self.edu_quotes.isChecked():
            self.use_file.setDisabled(False)
            if self.use_file.isChecked():
                self.file_button.setDisabled(False)
        else:
            self.use_file.setChecked(False)
            self.file_path.setReadOnly(False)
            self.file_path.clear()
            self.file_path.setReadOnly(True)
            self.use_file.setDisabled(True)
            self.file_button.setDisabled(True)

    def use_file_gui_changes(self):
        if self.use_file.isChecked():
            self.file_button.setDisabled(False)
        else:
            self.file_path.setReadOnly(False)
            self.file_path.clear()
            self.file_path.setReadOnly(True)
            self.file_button.setDisabled(True)

    def prefsPrep(self):
        from calibre.utils.config import JSONConfig
        plugin_prefs = JSONConfig('plugins/{0}_SmarterPunct_settings'.format(PLUGIN_SAFE_NAME))
        plugin_prefs.defaults['edu_quotes'] = True
        plugin_prefs.defaults['use_file'] = False
        plugin_prefs.defaults['file_path'] = ''
        plugin_prefs.defaults['dashes'] = 1
        plugin_prefs.defaults['ellipses'] = True
        plugin_prefs.defaults['unicode'] = True
        return plugin_prefs

    def savePrefs(self):
        self.prefs['edu_quotes'] = self.edu_quotes.isChecked()
        self.prefs['use_file'] = self.use_file.isChecked()
        self.prefs['file_path'] = unicode(self.file_path.displayText()) if len(self.file_path.displayText()) else ''
        self.prefs['dashes'] = self.dashes_combo.currentIndex()
        self.prefs['ellipses'] = self.ellipses.isChecked()
        self.prefs['unicode'] = self.unicode.isChecked()

    def help_link_activated(self, url):
        def get_help_file_resource():
            # Copy the HTML helpfile to the plugin directory each time the
            # link is clicked in case the helpfile is updated in newer plugins.
            file_path = os.path.join(config_dir, 'plugins', self.help_file_name)
            with open(file_path,'w') as f:
                f.write(load_resource('resources/{}'.format(self.help_file_name)))
            return file_path
        url = 'file:///' + get_help_file_resource()
        open_url(QUrl(url))

    def parseExceptionsFile(self, filename):
        import os, codecs, chardet
        words_list = []
        bytes = min(32, os.path.getsize(filename))
        raw = open(filename, 'rb').read(bytes)
        if raw.startswith(codecs.BOM_UTF8):
            enc = 'utf-8-sig'
        else:
            result = chardet.detect(raw)
            enc = result['encoding']
        try:
            with codecs.open(filename, encoding=enc, mode='r') as fd:
                words_list = [line.rstrip() for line in fd]
            words_list = filter(None, words_list)
            print('Exceptions list:', words_list)
        except:
            pass
        return words_list


class ShowProgressDialog(QProgressDialog):
    def __init__(self, gui, container, match_list, criteria, callback_fn, action_type='Checking'):
        self.file_list = [i[0] for i in container.mime_map.items() if i[1] in match_list]
        self.clean = True
        self.changed_files = []
        self.total_count = len(self.file_list)
        QProgressDialog.__init__(self, '', _('Cancel'), 0, self.total_count, gui)
        self.setMinimumWidth(500)
        self.container, self.criteria, self.callback_fn, self.action_type = container, criteria, callback_fn, action_type
        self.gui = gui
        self.setWindowTitle('{0}...'.format(self.action_type))
        self.i = 0
        QTimer.singleShot(0, self.do_action)
        self.exec_()

    def do_action(self):
        if self.wasCanceled():
            return self.do_close()
        if self.i >= self.total_count:
            return self.do_close()
        name = self.file_list[self.i]
        data = self.container.raw_data(name)
        orig_hash = md5(data).digest()
        self.i += 1

        self.setLabelText('{0}: {1}'.format(self.action_type, name))
        # Send the necessary data to the callback function in main.py.
        print('Processing {0}'.format(name))
        htmlstr = self.callback_fn(data, self.criteria)
        new_hash = md5(htmlstr).digest()
        if new_hash != orig_hash:
            self.container.open(name, 'wb').write(htmlstr)
            self.changed_files.append(name)
            self.clean = False

        self.setValue(self.i)

        # Lather, rinse, repeat
        QTimer.singleShot(0, self.do_action)

    def do_close(self):
        self.hide()
        self.gui = None

class ResultsDialog(Dialog):
    def __init__(self, parent, files):
        self.files = files
        Dialog.__init__(self, _('Changed Files'), 'toolbag_show_results_dialog', parent)

    def setup_ui(self):
        self.setMinimumWidth(300)
        self.setMinimumHeight(300)
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        main_layout = QHBoxLayout()
        layout.addLayout(main_layout)
        self.listy = QListWidget()
        # self.listy.setSelectionMode(QAbstractItemView.ExtendedSelection)
        main_layout.addWidget(self.listy)
        self.listy.addItems(self.files)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box = QDialogButtonBox()

        ok_button = button_box.addButton(_("See what changed"), QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton(_("Close"), QDialogButtonBox.RejectRole)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

def load_resource(name):
    with ZipFile(PLUGIN_PATH, 'r') as zf:
        if name in zf.namelist():
            return zf.read(name)
    return ''
