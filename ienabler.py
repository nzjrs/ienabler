#!/usr/bin/env python
# GUI for logging into the University of Canterbury internet
# Works like ienabler for the windows machines
#
# (c) John Stowers 2008

import telnetlib

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


