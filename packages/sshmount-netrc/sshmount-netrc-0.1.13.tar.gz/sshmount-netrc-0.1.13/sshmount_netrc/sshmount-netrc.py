#!/usr/bin/python

# Copyright (c) 2015 Tjaart van der Walt

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

"""
This script allows you to authenticate your sshfs connection using your .netrc
file. This is probably not the most secure way to do this, but it is very
convenient if you can't setup ssh-keys for the connection.
"""

import subprocess
import sys
import netrc
from os.path import expanduser
from os import system
from optparse import OptionParser

def parse_opts():
    netrc_path = expanduser("~") + "/.netrc"
    
    usage = "usage: %prog [options] server_name [user_name]"
    parser = OptionParser(usage=usage)
    parser.add_option("-m", "--mountpoint", dest="mountpoint",
                  metavar="MOUNTPOINT", help="The location to mount the filesystem")
    parser.add_option("-f", "--file", dest="filename", default=netrc_path,
                  metavar="NETRC", help="The location of your .netrc file")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  metavar="VERBOSE", help="Print debug information")
    (options, arguments) =  parser.parse_args()
    if(len(arguments) < 1):
        parser.print_help()
        print("")
        sys.exit(1)
    return (options, arguments)

def read_netrc(filename, host):
     my_netrc = netrc.netrc(filename)
     return my_netrc.authenticators(host)
     
def main():
    (options, arguments) = parse_opts()
    host = arguments[0]
    result = read_netrc(options.filename, host)
    if result is None:
        print("No matching password could be found for host: " + host, file=sys.stderr)
        exit(1)
    else:
        (login, account, password) = result

    user_host = login + "@" + host
    if options.mountpoint == None:
        mountpoint = expanduser("~") + "/mnt/" + user_host
    else:
        mountpoint = options.mountpoint

    system("mkdir -p " + mountpoint )

    # FIXME This is probably not the best way to do this!
    ret = system("echo " + password + " | sshfs -o password_stdin " + user_host + ": " + mountpoint)
    if ret == 0 and options.verbose:
        print("sshfs-netrc: '" + login + "@" + host + "' successfully mounted at '" + mountpoint + "'")

if __name__ == '__main__':
    main()
    
