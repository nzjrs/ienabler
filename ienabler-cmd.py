#!/usr/bin/env python
# Script for logging into the University of Canterbury internet
# Works like ienabler for the windows machines
#
# (c) John Stowers 2008

import sys
import getopt
import getpass
from ienabler import IEnabler

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



