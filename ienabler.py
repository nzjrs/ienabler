#!/usr/bin/env python
# GUI for logging into the University of Canterbury internet
# Works like ienabler for the windows machines
#
# (c) John Stowers 2008

import telnetlib

class IEnabler(object):
    def __init__(self,user,password, host="ienabler.canterbury.ac.nz", port=259):
        self.user = user
        self.password = password
        try:
            self.tn = telnetlib.Telnet(
                            host,
                            port
                            )
        except Exception, e:
            self.tn = None
            print "ERROR: %s" % e

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
        if self.tn:
            ok = self._choice(1)
            self.tn.close()
        else:
            ok = False
        return ok

    def disable(self):
        if self.tn:
            ok = self._choice(2)
            self.tn.close()
        else:
            ok = False
        return ok


