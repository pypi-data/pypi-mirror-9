#!/usr/bin/env python2

import os
import sys
import imp
import getpass
import fs_hopper
from optparse import OptionParser
from nodes import Node

def dummy():
    pass


class DoDit(object):
    def __init__(self, root, workflows):
        self.root = root
        self.workflows = workflows
        self.wf_modules = {}
        print "Connected to: %s" % root.dn
        self.wf_dir = fs_hopper.Directory(os.path.expanduser('~/.config/ldap_hopper'))
        for mod_file in self.wf_dir.get_childs('*.py'):
            mod_name = mod_file.name.split(os.path.sep)[-1].replace('.py', '')
            print "Loading workflow: %s" % mod_name,
            mod = imp.load_source(mod_name, mod_file.name)
            if (
                    hasattr(mod, 'root') and isinstance(mod.root, str)
            ) and (
                    hasattr(mod, 'run') and isinstance(mod.run, type(dummy))
            ):
                print '[ok]'
                self.wf_modules[mod_name] = mod
            else:
                print '[malformed]'
        print "Loaded %s workflow modules." % len(self.wf_modules)

    def run(self):
        for workflow in self.workflows:
            print "Processing workflow: %s" % workflow,
            if workflow not in self.wf_modules:
                print "[unknown]"
            else:
                wf = self.wf_modules[workflow]
                base = self.root.by_dn(wf.root)
                print "[%s]" % base.dn
                try:
                    wf.run(base)
                except KeyboardInterrupt:
                    print
                    print "Aborted workflow."



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-s', '--server', dest='server', help='ldap server', default='localhost')
    parser.add_option('-b', '--base', dest='base_dn', help='base-DN')
    parser.add_option('-D', '--bind', dest='bind_dn', help='bind-DN')
    (opts, args) = parser.parse_args()
    if opts.base_dn and opts.bind_dn and args:
        bind_pw = getpass.getpass("Password for %s: " % opts.bind_dn)
    else:
        print "Usage: %s -s <server> -b <base-dn> -D <bind-dn> <workflow>"
        sys.exit(1)
    root = Node(opts.server, opts.base_dn, opts.bind_dn, bind_pw)
    dodit = DoDit(root, args)
    dodit.run()
