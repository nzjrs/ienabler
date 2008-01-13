#!/usr/bin/env python
# GUI for logging into the University of Canterbury internet
# Works like ienabler for the windows machines
#
# (c) John Stowers 2008

import gtk
import gobject
import dbus, dbus.glib
import getpass
import sys
import telnetlib
import pynotify
import threading
import time
import telnetlib
import sys
import getopt
import getpass
import os.path
import ConfigParser

class Config(object):
    def __init__(self):
        self._file = open(os.path.join(os.environ["HOME"],".ienabler"),'w')
        self._config = ConfigParser.ConfigParser(defaults = {
                                            "NAME":"IEnabler",
                                            "USER":"jrs89",
                                            "PASSWORD":"rice2498",
                                            "DELAY_MS":"500"})
        try:
            self._config.readfp(self._file)
        except IOError:
            #empty file
            pass

    def get(self, key):
        return self._config.get('DEFAULT',key)

    def set(self, key, value):
        self._config.set('DEFAULT',key, value)

    def save(self):
        self._config.write(self._file)
        self._file.close()
CONFIGURATION = Config()

class IEnabler(object):
    def __init__(self,user,password):
        self.user = user
        self.password = password
        self.tn = telnetlib.Telnet(
                        "ienabler.canterbury.ac.nz",
                        259
                        )

    def _read_string(self, string):
        result = self.tn.read_until(string, 5)
        return result.endswith(string)

    def _login(self):
        if self._read_string("User: "):
            self.tn.write(self.user + "\n")
            if self._read_string("password: "):
                self.tn.write(self.password + "\n")
                return True
        return False

    def _choice(self,choice):
        try:
            if self._login():
                #returns the idx of the matched regex
                idx,match,txt = self.tn.expect(
                                    [r'.*Access denied.*',r'.*Enter your choice.*'],
                                    5
                                    )
                if idx == 1:
                    self.tn.write("%s\n" % choice)
                    if self._read_string('\n'):
                        return True
                else:
                    print "ERROR: %s" % txt
                    return False
        except EOFError:
            return False

    def enable(self):
        ok = self._choice(1)
        self.tn.close()
        return ok

    def disable(self):
        ok = self._choice(2)
        self.tn.close()
        return ok

class Authenticator(threading.Thread, gobject.GObject):
    __gsignals__ =  { 
                    "completed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_BOOLEAN,gobject.TYPE_STRING])
                    }

    def __init__(self, choice):
        gobject.GObject.__init__(self)
        threading.Thread.__init__(self)
        self.choice = choice

    def run(self):
        i = IEnabler(CONFIGURATION.get("USER"),CONFIGURATION.get("PASSWORD"))
        if self.choice == "Enable":
            ok = i.enable()
        else:
            ok = i.disable()
        self.emit("completed", ok, self.choice)

    def emit(self, *args):
        """
        Override the gobject signal emission so that signals
        can be emitted from threads
        """
        gobject.idle_add(gobject.GObject.emit,self,*args)

class NetworkListener(gobject.GObject):

    SERVICE_NAME = "org.freedesktop.NetworkManager"
    SERVICE_PATH = "/org/freedesktop/NetworkManager"

    __gsignals__ =  { 
                "online": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
                "offline": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
                }

    def __init__(self):
        gobject.GObject.__init__(self)
        self.online = False
        try:
                systemBus = dbus.SystemBus()
                proxy_obj = systemBus.get_object(NetworkListener.SERVICE_NAME,
                                                 NetworkListener.SERVICE_PATH)

                #magic number: aparently 3 == online
                self.online = int(proxy_obj.state()) == 3

                nm_interface = dbus.Interface(proxy_obj, NetworkListener.SERVICE_NAME)
                nm_interface.connect_to_signal('DeviceNowActive', self.active_cb)
                nm_interface.connect_to_signal('DeviceNoLongerActive', self.inactive_cb)
        except DBusException, de:
                print "Error while connecting to NetworkManager: %s" % str(de)

    def active_cb(self, path):
        self.online = True
        print "ONLINE"
        self.emit("online")

    def inactive_cb(self, path):
        print "OFFLINE"
        self.online = False
        self.emit("offline")


class Gui(object):
    def __init__(self):
        pynotify.init(CONFIGURATION.get("NAME"))
        self.online = False

        self._create_gui()
        self.nm = NetworkListener()
        self.nm.connect("online", lambda x: self.authenticate("Enable"))
        if self.nm.online:
            gobject.timeout_add(int(CONFIGURATION.get("DELAY_MS")),self.authenticate,"Enable")

    def _create_gui(self):
        #load themed or fallback app icon
        try:
            icon = os.path.join(os.path.dirname(__file__),'uclogo.svg')
            self.icon = gtk.gdk.pixbuf_new_from_file(icon)
        except gobject.GError:
            self.icon = gtk.icon_theme_get_default().load_icon(gtk.STOCK_NETWORK, 24, gtk.ICON_LOOKUP_FORCE_SVG)

        #build tray icon
        self.tray = gtk.StatusIcon()
        self.tray.set_from_pixbuf(self.icon)
        self.tray.set_tooltip('IEnabler Connecting..')
        self.tray.connect('popup-menu', self._on_popup_menu)
        self.tray.set_visible(True)

        #attach the libnotification bubble to the tray
        self.notification = pynotify.Notification(CONFIGURATION.get("NAME"))
        self.notification.attach_to_status_icon(self.tray)
        self.notification.set_timeout(pynotify.EXPIRES_DEFAULT)
        
        #create popup menu
        self.menu = gtk.Menu()
        enable = gtk.ImageMenuItem(stock_id=gtk.STOCK_YES, accel_group=None)
        enable.connect("activate", lambda x: self.authenticate("Enable"))
        disable = gtk.ImageMenuItem(stock_id=gtk.STOCK_NO, accel_group=None)
        disable.connect("activate", lambda x: self.authenticate("Disable"))
        about = gtk.ImageMenuItem(stock_id=gtk.STOCK_ABOUT, accel_group=None)
        about.connect("activate", self._on_about_clicked)
        quit = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT, accel_group=None)
        quit.connect("activate", self._on_exit_clicked)
        
        self.menu.add(enable)
        self.menu.add(disable)
        self.menu.add(gtk.SeparatorMenuItem())
        self.menu.add(about)
        self.menu.add(quit)
        self.menu.show_all()

    def _on_popup_menu(self, status, button, time):
        self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.tray)

    def _on_about_clicked(self, widget):
        about = gtk.AboutDialog()
        about.set_name(CONFIGURATION.get("NAME"))
        about.set_logo(self.icon)
        about.set_authors(("John Stowers",))
        about.set_comments("Log to the University of Canterbury Internet")
        about.run()
        about.destroy()

    def _on_exit_clicked(self, widget):
        if self.is_online():
            self.authenticate("Disable", block=True)
        CONFIGURATION.save()
        gtk.main_quit()

    def _on_authenticated(self, authenticator, ok, choice):
        if ok:
            msg = "Internet Access %sd OK" % choice
            self.online = choice == "Enable"
            self.tray.set_tooltip('Internet %sd' % choice)
        else:
            msg = "Could not %s Internet Access" % choice
            self.online = False
        self.notification.update(CONFIGURATION.get("NAME"),msg,gtk.STOCK_NETWORK)
        self.notification.show()
                
    def authenticate(self, choice, block=False):
        authenticator = Authenticator(choice)
        authenticator.connect("completed", self._on_authenticated)
        authenticator.start()
        if block:
            authenticator.join()

    def is_online(self):
        return self.nm.online and self.online

if __name__ == "__main__":
    gtk.gdk.threads_init()
    app = Gui()
    gtk.main()



