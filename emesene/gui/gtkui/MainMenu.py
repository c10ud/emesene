# -*- coding: utf-8 -*-

#    This file is part of emesene.
#
#    emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    emesene is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with emesene; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
import e3
import gui
from gui.gtkui import check_gtk3
import utils
import sys

import extension

class MainMenu(gtk.MenuBar):
    """
    A widget that represents the main menu of the main window
    """
    NAME = 'Main Menu'
    DESCRIPTION = 'The Main Menu of the main window'
    AUTHOR = 'Mariano Guerra'
    WEBSITE = 'www.emesene.org'

    def __init__(self, handlers, session):
        """
        constructor

        handlers is a e3common.Handler.MenuHandler
        """
        gtk.MenuBar.__init__(self)

        FileMenu = extension.get_default('menu file')
        ActionsMenu = extension.get_default('menu actions')
        OptionsMenu = extension.get_default('menu options')
        HelpMenu = extension.get_default('menu help')

        file_ = gtk.MenuItem(_('_File'))
        self.file_menu = FileMenu(handlers.file_handler, session)
        file_.set_submenu(self.file_menu)

        actions = gtk.MenuItem(_('_Actions'))
        actions_menu = ActionsMenu(handlers.actions_handler, session)
        actions.set_submenu(actions_menu)

        options = gtk.MenuItem(_('_Options'))
        options_menu = OptionsMenu(handlers.options_handler, session.config)
        options.set_submenu(options_menu)

        help = gtk.MenuItem(_('_Help'))
        help_menu = HelpMenu(handlers.help_handler)
        help.set_submenu(help_menu)

        self.append(file_)
        self.append(actions)
        self.append(options)
        self.append(help)

    def set_accels(self, accel_group):
        """
        Set accelerators for menu items
        """
        self.file_menu.set_accels(accel_group)

    def remove_subscriptions(self):
        self.file_menu.remove_subscriptions()

class EndPointsMenu(gtk.Menu):
    """
    A widget that contains all the endpoints
    """
    def __init__(self, handler, session):
        """
        constructor

        handler -- e3common.Handler.FileHandler
        """
        gtk.Menu.__init__(self)
        self.handler = handler
        self.session = session

        self.ep_dict = {}
        ep_item = gtk.MenuItem(_('All other endpoints'))
        ep_item.connect('activate',
                lambda *args : self.handler.on_disconnect_endpoint_selected(""))
        self.append(ep_item)
        self.append(gtk.SeparatorMenuItem())

        self.session.signals.endpoint_added.subscribe(self.endpoint_added)
        self.session.signals.endpoint_removed.subscribe(self.endpoint_removed)
        self.session.signals.endpoint_updated.subscribe(self.endpoint_updated)

    def endpoint_added(self, ep_id, ep_name):
        ep_item = gtk.MenuItem(ep_name)
        ep_item.connect('activate',
            lambda *args: self.handler.on_disconnect_endpoint_selected(ep_id))
        ep_item.show()
        self.append(ep_item)
        self.ep_dict[ep_id] = ep_item

    def endpoint_removed(self, ep_id):
        if ep_id in self.ep_dict:
            self.ep_dict[ep_id].hide()
            del self.ep_dict[ep_id]

    def endpoint_updated(self, ep_id, ep_name):
        if ep_id in self.ep_dict:
            self.ep_dict[ep_id].set_label(ep_name)

    def remove_subscriptions(self):
        self.session.signals.endpoint_added.unsubscribe(self.endpoint_added)
        self.session.signals.endpoint_removed.unsubscribe(self.endpoint_removed)
        self.session.signals.endpoint_updated.unsubscribe(self.endpoint_updated)

class FileMenu(gtk.Menu):
    """
    A widget that represents the File popup menu located on the main menu
    """

    def __init__(self, handler, session):
        """
        constructor

        handler -- e3common.Handler.FileHandler
        """
        gtk.Menu.__init__(self)
        self.session = session

        self.ep_dict = {}

        if session and session.session_has_service(e3.Session.SERVICE_STATUS):
            StatusMenu = extension.get_default('menu status')
            status = gtk.ImageMenuItem(_('Status'))
            status.set_image(gtk.image_new_from_stock(gtk.STOCK_CONVERT,
                gtk.ICON_SIZE_MENU))
            status_menu = StatusMenu(handler.on_status_selected)
            status.set_submenu(status_menu)
            self.append(status)

        if session and session.session_has_service(e3.Session.SERVICE_ENDPOINTS):
            self.ep = gtk.MenuItem(_('Disconnect endpoints'))
            self.ep_menu = EndPointsMenu(handler, session)
            self.ep.set_submenu(self.ep_menu)
            self.append(self.ep)
            # set ep_menu hide by default and ignore show_all when init
            self.ep_menu.show_all()
            self.ep.hide()
            self.ep.set_no_show_all(True)

            self.session.signals.endpoint_added.subscribe(self.ep_menu_display)
            self.session.signals.endpoint_removed.subscribe(self.ep_menu_display)

        self.disconnect = gtk.ImageMenuItem(gtk.STOCK_DISCONNECT)
        self.disconnect.connect('activate',
            lambda *args: handler.on_disconnect_selected())
        self.quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.quit.connect('activate',
            lambda *args: handler.on_quit_selected())

        self.append(self.disconnect)
        self.append(gtk.SeparatorMenuItem())
        self.append(self.quit)

    def set_accels(self, accel_group):
        if sys.platform == 'darwin':
            self.quit.add_accelerator(
                    'activate', accel_group, gtk.keysyms.Q,
                    gtk.gdk.META_MASK, gtk.ACCEL_VISIBLE)
            self.disconnect.add_accelerator(
                    'activate', accel_group, gtk.keysyms.D,
                    gtk.gdk.META_MASK, gtk.ACCEL_VISIBLE)
        else:
            self.quit.add_accelerator(
                    'activate', accel_group, gtk.keysyms.Q,
                    gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
            self.disconnect.add_accelerator(
                    'activate', accel_group, gtk.keysyms.D,
                    gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

    def ep_menu_display(self, ep_id, ep_name=None):
        '''called when signal changed'''
        if self.ep_menu:
            # only added signal with valid name
            if ep_name is not None:
                self.ep_dict[ep_id] = True
            elif ep_id in self.ep_dict:
                del self.ep_dict[ep_id]
            self.ep.set_visible(len(self.ep_dict) > 0)

    def remove_subscriptions(self):
        if self.session and self.session.session_has_service(e3.Session.SERVICE_ENDPOINTS):
            self.ep_menu.remove_subscriptions()

            self.session.signals.endpoint_added.unsubscribe(self.ep_menu_display)
            self.session.signals.endpoint_removed.unsubscribe(self.ep_menu_display)

class ActionsMenu(gtk.Menu):
    """
    A widget that represents the Actions popup menu located on the main menu
    """

    def __init__(self, handler, session):
        """
        constructor

        handler -- e3common.Handler.ActionsHandler
        """
        gtk.Menu.__init__(self)

        ContactsMenu = extension.get_default('menu contact')
        AccountMenu = extension.get_default('menu account')

        contact = gtk.ImageMenuItem(_('_Contact'))
        contact.set_image(utils.safe_gtk_image_load(gui.theme.image_theme.chat))
        contact_menu = ContactsMenu(handler.contact_handler, session)
        contact.set_submenu(contact_menu)
        account = gtk.ImageMenuItem(_('_Account'))
        account.set_image(utils.safe_gtk_image_load(gui.theme.image_theme.chat))

        account_menu = AccountMenu(handler.my_account_handler)
        myaccount = gtk.ImageMenuItem(_('_Profile'))
        myaccount.set_image(utils.safe_gtk_image_load(gui.theme.image_theme.chat))
        myaccount.set_submenu(account_menu)

        self.append(contact)

        if session.session_has_service(e3.Session.SERVICE_GROUP_MANAGING):
            GroupsMenu = extension.get_default('menu group')
            group = gtk.ImageMenuItem(_('_Group'))
            group.set_image(utils.safe_gtk_image_load(gui.theme.image_theme.group_chat))
            group_menu = GroupsMenu(handler.group_handler)
            group.set_submenu(group_menu)
            self.append(group)

        self.append(myaccount)

class OptionsMenu(gtk.Menu):
    """
    A widget that represents the Options popup menu located on the main menu
    """

    def __init__(self, handler, config):
        """
        constructor

        handler -- e3common.Handler.OptionsHandler
        """
        gtk.Menu.__init__(self)

        if not check_gtk3():
            by_status = gtk.RadioMenuItem(None, _('Order by _status'))
            by_group = gtk.RadioMenuItem(by_status, _('Order by _group'))
        else:
            by_status = gtk.RadioMenuItem(_('Order by _status'))
            by_status.set_use_underline(True)
            by_group = gtk.RadioMenuItem.new_with_mnemonic_from_widget(by_status, _('Order by _group'))
        by_group.set_active(config.b_order_by_group)
        by_status.set_active(not config.b_order_by_group)

        show_menu = gtk.MenuItem(_('Show...'))
        show_submenu = gtk.Menu()

        show_offline = gtk.CheckMenuItem(_('Show _offline contacts'))
        show_offline.set_active(config.b_show_offline)
        group_offline = gtk.CheckMenuItem(_('G_roup offline contacts'))
        group_offline.set_active(config.b_group_offline)
        show_empty_groups = gtk.CheckMenuItem(_('Show _empty groups'))
        show_empty_groups.set_active(config.b_show_empty_groups)
        show_blocked = gtk.CheckMenuItem(_('Show _blocked contacts'))
        show_blocked.set_active(config.b_show_blocked)
        sort_by_name = gtk.CheckMenuItem(_('Sort contacts by _name'))
        sort_by_name.set_active(config.b_order_by_name)

        preferences = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        preferences.connect('activate',
            lambda *args: handler.on_preferences_selected())

        by_status.connect('toggled',
            lambda *args: handler.on_order_by_status_toggled(
                by_status.get_active()))
        by_group.connect('toggled',
            lambda *args: handler.on_order_by_group_toggled(
                by_group.get_active()))
        show_empty_groups.connect('toggled',
            lambda *args: handler.on_show_empty_groups_toggled(
                show_empty_groups.get_active()))
        show_offline.connect('toggled',
            lambda *args: handler.on_show_offline_toggled(
                show_offline.get_active()))
        group_offline.connect('toggled',
            lambda *args: handler.on_group_offline_toggled(
                group_offline.get_active()))
        show_blocked.connect('toggled',
            lambda *args: handler.on_show_blocked_toggled(
                show_blocked.get_active()))
        sort_by_name.connect('toggled',
            lambda *args: handler.on_order_by_name_toggled(
                sort_by_name.get_active()))

        show_menu.set_submenu(show_submenu)
        show_submenu.append(show_offline)
        show_submenu.append(show_blocked)
        show_submenu.append(show_empty_groups)

        self.append(by_status)
        self.append(by_group)
        self.append(gtk.SeparatorMenuItem())
        self.append(show_menu)
        self.append(sort_by_name)
        self.append(group_offline)
        self.append(gtk.SeparatorMenuItem())
        self.append(preferences)

class HelpMenu(gtk.Menu):
    """
    A widget that represents the Help popup menu located on the main menu
    """

    def __init__(self, handler):
        """
        constructor

        handler -- e3common.Handler.HelpHandler
        """
        gtk.Menu.__init__(self)

        website = gtk.ImageMenuItem(_('_Website'))
        website.set_image(gtk.image_new_from_stock(gtk.STOCK_HOME,
            gtk.ICON_SIZE_MENU))
        website.connect('activate',
            lambda *args: handler.on_website_selected())
        about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        about.connect('activate',
            lambda *args: handler.on_about_selected())

        debug = gtk.MenuItem(_('Debug'))
        debug.connect('activate',
                lambda *args: handler.on_debug_selected())
                
        updatecheck = gtk.ImageMenuItem(_('Check for updates'))
        updatecheck.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH,
            gtk.ICON_SIZE_MENU))
        updatecheck.connect('activate', lambda *args: handler.on_check_update_selected())

        self.append(website)
        self.append(about)
        self.append(debug)
        self.append(gtk.SeparatorMenuItem())
        self.append(updatecheck)
