# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

try:
    from PyQt5.Qt import QAction, QMenu, QDialog, QIcon, QPixmap
except:
    from PyQt4.Qt import QAction, QMenu, QDialog, QIcon, QPixmap

import os

from calibre.gui2.tweak_book.plugin import Tool
from calibre.gui2.tweak_book import editor_name
from calibre.gui2 import error_dialog, info_dialog
from calibre.ebooks.oeb.polish.container import OEB_DOCS, OEB_STYLES

from calibre.utils.config import JSONConfig, config_dir
from calibre_plugins.diaps_toolbag.resources.html_parser import MarkupParser
from calibre_plugins.diaps_toolbag.resources.smartypants import smartyPants
from calibre_plugins.diaps_toolbag.utilities import unescape
from calibre_plugins.diaps_toolbag.dialogs import ResultsDialog

from calibre_plugins.diaps_toolbag.__init__ import PLUGIN_SAFE_NAME

def get_icon(icon_name):

    # Check to see whether the icon exists as a Calibre resource
    # This will enable skinning if the user stores icons within a folder like:
    # ...\AppData\Roaming\calibre\resources\images\Plugin Name\
    icon_path = os.path.join(config_dir, 'resources', 'images', 'Diaps Editing Toolbag',
                             icon_name.replace('images/', ''))
    if os.path.exists(icon_path):
        pixmap = QPixmap()
        pixmap.load(icon_path)
        return QIcon(pixmap)
    # As we did not find an icon elsewhere, look within our zip resources
    return get_icons(icon_name)


# pulls in translation files for _() strings
try:
    load_translations()
except NameError:
    pass  # load_translations() added in calibre 1.9

class SpanDivEdit(Tool):
    name = 'SpanDivEdit'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        self.plugin_prefs = JSONConfig('plugins/{0}_SpanDivEdit'.format(PLUGIN_SAFE_NAME))
        self.plugin_prefs.defaults['parse_current'] = True

        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icon('images/spandivedit_icon.png'), _('Edit Spans && Divs'), self.gui)
        self.restore_prefs()
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'edit-spans-divs', default_keys=('Ctrl+Shift+Alt+E',))
        else:
            menu = QMenu()
            ac.setMenu(menu)
            checked_menu_item = menu.addAction(_('Edit current file only'), self.toggle_parse_current)
            checked_menu_item.setCheckable(True)
            checked_menu_item.setChecked(self.parse_current)
            menu.addSeparator()
            config_menu_item = menu.addAction(_('Customize'), self.show_configuration)
        ac.triggered.connect(self.dispatcher)
        return ac

    def toggle_parse_current(self):
        self.parse_current = not self.parse_current
        self.save_prefs()

    def dispatcher(self):
        container = self.current_container  # The book being edited as a container object
        if not container:
            return info_dialog(self.gui, _('No book open'),
                        _('Need to have a book open first.'), show=True)
        if self.parse_current:
            name = editor_name(self.gui.central.current_editor)
            if not name or container.mime_map[name] not in OEB_DOCS:
                return info_dialog(self.gui, _('Cannot Process'),
                        _('No file open for editing or the current file is not an (x)html file.'), show=True)

        self.cleanasawhistle = True
        self.changed_files = []

        from calibre_plugins.diaps_toolbag.dialogs import RemoveDialog
        dlg = RemoveDialog(self.gui)
        if dlg.exec_():
            criteria = dlg.getCriteria()

            # Ensure any in progress editing the user is doing is present in the container
            self.boss.commit_all_editors_to_container()
            self.boss.add_savepoint(_('Before: Span Div Edit'))

            try:
                self.process_files(criteria)
            except Exception:
                # Something bad happened report the error to the user
                import traceback
                error_dialog(self.gui, _('Failed'),
                    _('Failed to process divs or spans, click "Show details" for more info'),
                    det_msg=traceback.format_exc(), show=True)
                # Revert to the saved restore point
                self.boss.revert_requested(self.boss.global_undo.previous_container)
            else:
                if not self.cleanasawhistle:
                    # Show the user what changes we have made,
                    # allowing then to revert them if necessary
                    accepted = ResultsDialog(self.gui, self.changed_files).exec_()
                    if accepted == QDialog.Accepted:
                        self.boss.show_current_diff()
                    # Update the editor UI to take into account all the changes we
                    # have made
                    self.boss.apply_container_update_to_gui()
                else:
                    info_dialog(self.gui, _('Nothing changed'),
                    '<p>{0}'.format(_('Nothing matching your criteria was found.')), show=True)

    def process_files(self, criteria):
        container = self.current_container  # The book being edited as a container object

        if self.parse_current:
            name = editor_name(self.gui.central.current_editor)
            data = container.raw_data(name)
            htmlstr = self.delete_modify(data, criteria)
            if htmlstr != data:
                self.cleanasawhistle = False
                container.open(name, 'wb').write(htmlstr)
        else:
            from calibre_plugins.diaps_toolbag.dialogs import ShowProgressDialog
            d = ShowProgressDialog(self.gui, container, OEB_DOCS, criteria, self.delete_modify, _('Parsing'))
            self.cleanasawhistle = d.clean
            self.changed_files.extend(d.changed_files)

    def delete_modify(self, data, criteria):
        _parser = MarkupParser(data, srch_str=criteria[0], srch_method=criteria[1], tag=criteria[2], attrib=criteria[3],
                               action=criteria[4], new_tag=criteria[5], new_str=criteria[6], copy=criteria[7])

        htmlstr = _parser.processml()
        return htmlstr

    def show_configuration(self):
        from calibre_plugins.diaps_toolbag.span_div_config import ConfigWidget
        dlg = ConfigWidget(self.gui)
        if dlg.exec_():
            pass

    def restore_prefs(self):
        self.parse_current = self.plugin_prefs.get('parse_current')

    def save_prefs(self):
        self.plugin_prefs['parse_current'] = self.parse_current


class SmarterPunct(Tool):
    name = 'SmarterPunct'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        self.plugin_prefs = JSONConfig('plugins/{0}_SmarterPunct'.format(PLUGIN_SAFE_NAME))
        self.plugin_prefs.defaults['parse_current'] = True

        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icon('images/smarten_icon.png'), _('Smarten Punctuation (the sequel)'), self.gui)
        self.restore_prefs()
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'smarter-punctuation', default_keys=('Ctrl+Shift+Alt+S',))
        menu = QMenu()
        ac.setMenu(menu)
        checked_menu_item = menu.addAction(_('Smarten current file only'), self.toggle_parse_current)
        checked_menu_item.setCheckable(True)
        checked_menu_item.setChecked(self.parse_current)
        ac.triggered.connect(self.dispatcher)
        return ac

    def toggle_parse_current(self):
        self.parse_current = not self.parse_current
        self.save_prefs()

    def dispatcher(self):
        container = self.current_container  # The book being edited as a container object
        if not container:
            return info_dialog(self.gui, _('No book open'),
                        _('Need to have a book open first.'), show=True)
        if self.parse_current:
            name = editor_name(self.gui.central.current_editor)
            if not name or container.mime_map[name] not in OEB_DOCS:
                return info_dialog(self.gui, _('Cannot Process'),
                        _('No file open for editing or the current file is not an (x)html file.'), show=True)

        self.cleanasawhistle = True
        self.changed_files = []

        from calibre_plugins.diaps_toolbag.dialogs import PunctDialog
        dlg = PunctDialog(self.gui)
        if dlg.exec_():
            criteria = dlg.getCriteria()
            # Ensure any in progress editing the user is doing is present in the container
            self.boss.commit_all_editors_to_container()
            self.boss.add_savepoint(_('Before: Smarten Punctuation'))

            try:
                self.process_files(criteria)
            except Exception:
                # Something bad happened report the error to the user
                import traceback
                error_dialog(self.gui, _('Failed'),
                    _('Failed to smarten punctuation, click "Show details" for more info'),
                    det_msg=traceback.format_exc(), show=True)
                # Revert to the saved restore point
                self.boss.revert_requested(self.boss.global_undo.previous_container)
            else:
                if not self.cleanasawhistle:
                    # Show the user what changes we have made,
                    # allowing then to revert them if necessary
                    accepted = ResultsDialog(self.gui, self.changed_files).exec_()
                    if accepted == QDialog.Accepted:
                        self.boss.show_current_diff()
                    # Update the editor UI to take into account all the changes we
                    # have made
                    self.boss.apply_container_update_to_gui()
                else:
                    info_dialog(self.gui, _('Nothing smartened'),
                    '<p>{0}'.format(_('No punctuation meeting your criteria was found to smarten.')), show=True)

    def process_files(self, criteria):
        container = self.current_container  # The book being edited as a container object
        if self.parse_current:
            name = editor_name(self.gui.central.current_editor)
            data = container.raw_data(name)
            htmlstr = self.smarten(data, criteria)
            if htmlstr != data:
                self.cleanasawhistle = False
                container.open(name, 'wb').write(htmlstr)
        else:
            from calibre_plugins.diaps_toolbag.dialogs import ShowProgressDialog
            d = ShowProgressDialog(self.gui, container, OEB_DOCS, criteria, self.smarten, _('Smartening'))
            cancelled_msg = ''
            if d.wasCanceled():
                cancelled_msg = ' (cancelled)'
            self.cleanasawhistle = d.clean
            self.changed_files.extend(d.changed_files)

    def smarten(self, data, criteria):
        from uuid import uuid4
        AMPERSAND = 'ampersand-{0}'.format(str(uuid4()))
        smarty_attr, use_unicode, apos_words_list = criteria[0], criteria[1], criteria[2]

        # Slightly mangle all preexisting entities so HTMLParser
        # ignores them. We'll put them all back at the end.
        data = data.replace('&', AMPERSAND)

        htmlstr = smartyPants(data, smarty_attr, AMPERSAND, apos_words_list)

        #  Convert the entities we created to unicode characters
        if use_unicode:
            htmlstr = unescape(htmlstr)
        # Unmangle the pre-existing entities
        htmlstr = htmlstr.replace(AMPERSAND, '&')

        return htmlstr

    def restore_prefs(self):
        self.parse_current = self.plugin_prefs.get('parse_current')

    def save_prefs(self):
        self.plugin_prefs['parse_current'] = self.parse_current


class CSScm2em(Tool):
    name = 'CSScm2em'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        self.plugin_prefs = JSONConfig('plugins/{0}_CSScm2em'.format(PLUGIN_SAFE_NAME))
        self.plugin_prefs.defaults['parse_current'] = True

        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction(get_icon('images/css_icon.png'), _('Convert CSS cm to em'), self.gui)
        self.restore_prefs()
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'css-cms-to-ems', default_keys=('Ctrl+Shift+Alt+C',))
        menu = QMenu()
        ac.setMenu(menu)
        checked_menu_item = menu.addAction(_('Convert current CSS file only'), self.toggle_parse_current)
        checked_menu_item.setCheckable(True)
        checked_menu_item.setChecked(self.parse_current)
        ac.triggered.connect(self.dispatcher)
        return ac

    def toggle_parse_current(self):
        self.parse_current = not self.parse_current
        self.save_prefs()

    def dispatcher(self):
        container = self.current_container
        if not container:
            return info_dialog(self.gui, _('No book open'),
                        _('Need to have a book open first.'), show=True)
        if self.parse_current:
            name = editor_name(self.gui.central.current_editor)
            if not name or container.mime_map[name] not in OEB_STYLES:
                return info_dialog(self.gui, _('Cannot Process'),
                        _('No file open for editing or the current file is not a CSS file.'), show=True)

        self.cleanasawhistle = True
        self.changed_files = []

        self.boss.commit_all_editors_to_container()
        self.boss.add_savepoint(_('Before: Convert CM to EM'))

        try:
            self.process_files()
        except Exception:
            # Something bad happened report the error to the user
            import traceback
            error_dialog(self.gui, _('Failed'),
                _('Failed to convert CMs to EMs, click "Show details" for more info'),
                det_msg=traceback.format_exc(), show=True)
            # Revert to the saved restore point
            self.boss.revert_requested(self.boss.global_undo.previous_container)
        else:
            if not self.cleanasawhistle:
                # Show the user what changes we have made,
                # allowing then to revert them if necessary
                accepted = ResultsDialog(self.gui, self.changed_files).exec_()
                if accepted == QDialog.Accepted:
                    self.boss.show_current_diff()
                # Update the editor UI to take into account all the changes we
                # have made
                self.boss.apply_container_update_to_gui()
            else:
                info_dialog(self.gui, _('Nothing Converted'),
                '<p>{0}'.format(_('No CM dimensions were found to convert.')), show=True)

    def process_files(self):
        def cssparse(sheet):
            SHEET_DIRTY = False
            for rule in sheet.cssRules:
                if rule.type in (rule.STYLE_RULE, rule.PAGE_RULE):
                    for property in rule.style:
                        val = property.propertyValue
                        for x in val:
                            if x.type == 'DIMENSION' and x.dimension == 'cm':
                                SHEET_DIRTY = True
                                x.cssText = self.convertcm2em(x.value) + 'em'
            if SHEET_DIRTY:
                self.cleanasawhistle = False
                self.changed_files.append(name)
                container.dirty(name)
        container = self.current_container  # The book being edited as a container object
        if self.parse_current:
            name = editor_name(self.gui.central.current_editor)
            sheet = container.parsed(name)
            cssparse(sheet)
        else:
            for name, mt in container.mime_map.iteritems():
                if mt in OEB_STYLES:
                    sheet = container.parsed(name)
                    cssparse(sheet)

    def restore_prefs(self):
        self.parse_current = self.plugin_prefs.get('parse_current')

    def save_prefs(self):
        self.plugin_prefs['parse_current'] = self.parse_current

    def convertcm2em(self, value):
        conv=2.37106301584
        return '%.2f' % (conv*float(value))
