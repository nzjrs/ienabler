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
    HOST = "ienabler.canterbury.ac.nz"
    PORT = "259"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "du:p:h:P:", ["disable", "user", "password", "host", "port"])
    except getopt.GetoptError:
        print   "Ienabler: Enables and Disables UOC Internet Access.\n" + \
                "Usage:\n" + \
                " ienabler [OPTIONS]\n" + \
                "Options:\n" + \
                " -d,--disable   Logs you out of the internet\n" + \
                " -u,--user      Username\n" + \
                " -p,--pasword   Password\n" + \
                " -h,--host      ienabler host\n" + \
                " -P,--port      ienabler port\n"
        sys.exit(1)

    choice = "Enable"
    for o, a in opts:
        if o in ("-d", "--disable"):
            choice = "Disable"
        if o in ("-u", "--user"):
            USER = a
        if o in ("-p", "--password"):
            PASSWORD = a
        if o in ("-h", "--host"):
            HOST = a
        if o in ("-P", "--port"):
            PORT = a


    if USER == "":
        USER = raw_input("Username:")
    if PASSWORD == "":
        PASSWORD = getpass.getpass("Password:")

    i = IEnabler(USER,PASSWORD,HOST,PORT)
    if choice == "Enable":
        ok = i.enable()
    else:
        ok = i.disable()

    if ok:
        print "%sd OK" % choice
    else:
        print "Could not %s" % choice
        sys.exit(1)



