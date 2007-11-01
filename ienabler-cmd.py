#!/usr/bin/env python
# Script for logging into the University of Canterbury internet
# Works like ienabler for the windows machines
#
# (c) John Stowers 2008

import telnetlib
import sys
import getopt
import getpass

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

if __name__ == "__main__":
    #FILL IN DEFAULTS IF YOU WANT
    USER = ""
    PASSWORD = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "du:p:", ["disable", "user", "password"])
    except getopt.GetoptError:
        print   "Ienabler: Enables and Disables UOC Internet Access.\n" + \
                "Usage:\n" + \
                " ienabler [OPTIONS]\n" + \
                "Options:\n" + \
                " -d,--disable   Logs you out of the internet\n" + \
                " -u,--user      Username\n" + \
                " -p,--pasword   Password\n"
        sys.exit(1)

    choice = "Enable"
    for o, a in opts:
        if o in ("-d", "--disable"):
            choice = "Disable"
        if o in ("-u", "--user"):
            USER = a
        if o in ("-p", "--password"):
            PASSWORD = a

    if USER == "":
        USER = raw_input("Username:")
    if PASSWORD == "":
        PASSWORD = getpass.getpass("Password:")

    i = IEnabler(USER,PASSWORD)
    if choice == "Enable":
        ok = i.enable()
    else:
        ok = i.disable()

    if ok:
        print "%sd OK" % choice
    else:
        print "Could not %s" % choice
        sys.exit(1)



