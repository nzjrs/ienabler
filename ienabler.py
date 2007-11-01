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

NAME="IEnabler"
ICON=gtk.STOCK_NETWORK
USER="jrs89"
PASSWORD="rice2498"

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
        i = IEnabler(USER,PASSWORD)
        if self.choice == "Enable":
            ok = i.enable()
        else:
            ok = i.disable()
        if ok:
            msg = "%sd OK" % self.choice
        else:
            msg = "Could not %s" % self.choice
        self.emit("completed", ok, msg)

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


class App:
    def __init__(self):
        pynotify.init(NAME)
        self.authenticator = None

        self.tray = self.create_icon()
        self.menu = self.create_menu()

        self.nm = NetworkListener()
        self.nm.connect("online", lambda x: self.authenticate("Enable"))
        if self.nm.online:
            gobject.timeout_add(1000,self.authenticate,"Enable")

    def _on_popup_menu(self, status, button, time):
        self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.tray)

    def _on_about_clicked(self, widget):
        about = gtk.AboutDialog()
        about.set_name(NAME)
        about.set_authors(("John Stowers",))
        about.set_comments("Log to the University of Canterbury Internet")
        about.run()
        about.destroy()

    def _on_exit_clicked(self, widget):
        gtk.main_quit()

    def _on_authenticated(self, authenticator, ok, msg):
        n = pynotify.Notification(NAME, msg, ICON)
        n.attach_to_status_icon(self.tray)
        n.show()
                
    def authenticate(self, choice):
        self.authenticator = Authenticator(choice)
        self.authenticator.connect("completed", self._on_authenticated)
        self.authenticator.start()            

    def create_icon(self):
        tray = gtk.StatusIcon()
        tray.set_from_stock(ICON)
        tray.set_tooltip('Ienabler')
        tray.connect('popup-menu', self._on_popup_menu)
        tray.set_visible(True)
        return tray
        
    # Creates the Contextual Menu    
    def create_menu(self):
        menu = gtk.Menu()
        enable = gtk.ImageMenuItem(stock_id=gtk.STOCK_YES, accel_group=None)
        enable.connect("activate", lambda x: self.authenticate("Enable"))
        disable = gtk.ImageMenuItem(stock_id=gtk.STOCK_NO, accel_group=None)
        disable.connect("activate", lambda x: self.authenticate("Disable"))
        about = gtk.ImageMenuItem(stock_id=gtk.STOCK_ABOUT, accel_group=None)
        about.connect("activate", self._on_about_clicked)
        quit = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT, accel_group=None)
        quit.connect("activate", self._on_exit_clicked)
        
        menu.add(enable)
        menu.add(disable)
        menu.add(gtk.SeparatorMenuItem())
        menu.add(about)
        menu.add(quit)
             
        menu.show_all()
        return menu

if __name__ == "__main__":
    gtk.gdk.threads_init()
    app = App()
    gtk.main()



