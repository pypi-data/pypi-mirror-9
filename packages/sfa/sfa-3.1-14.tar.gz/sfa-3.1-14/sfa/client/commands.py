#!/usr/bin/env python
import sys
import copy
from optparse import OptionParser
from argparse import ArgumentParser

from sfa.client.candidates import Candidates


def add_options(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('add_options', []).insert(0, (args, kwargs))
        return func
    return _decorator

class Commands(object):
    def _get_commands(self):
        command_names = []
        for attrib in dir(self):
            if callable(getattr(self, attrib)) and not attrib.startswith('_'):
                command_names.append(attrib)
        return command_names


class RegistryCommands(Commands):
    def __init__(self, *args, **kwds):
        print 'RegistryCommands.__init__','args',args,'kwds',kwds
 
    @add_options('-x', '--xrn', dest='xrn', metavar='<xrn>', help='authority to list (hrn/urn - mandatory)') 
    @add_options('-t', '--type', dest='type', metavar='<type>', help='object type', default='all') 
    @add_options('-r', '--recursive', dest='recursive', metavar='<recursive>', help='list all child records', 
                 action='store_true', default=False)
    @add_options('-v', '--verbose', dest='verbose', action='store_true', default=False)
    def list(self, xrn, type=None, recursive=False, verbose=False):
        """List names registered at a given authority - possibly filtered by type"""
        print 'RegistryCommands.list','xrn',xrn,'type',type,'recursive',recursive,'verbose',verbose


class SfaAdmin:

    def __init__ (self): pass

    CATEGORIES = {
#        'certificate': CertCommands,
        'registry': RegistryCommands,
#        'aggregate': AggregateCommands,
#        'slicemgr': SliceManagerCommands
    }

    # returns (name,class) or (None,None)
    def find_category (self, input):
        full_name=Candidates (SfaAdmin.CATEGORIES.keys()).only_match(input)
        if not full_name: return (None,None)
        return (full_name,SfaAdmin.CATEGORIES[full_name])

    def summary_usage (self, category=None):
        print 'usage..'
        sys.exit(2)

    def main (self):
        argv = copy.deepcopy(sys.argv)
        self.script_name = argv.pop(0)
        # ensure category is specified    
        if len(argv) < 1:
            self.summary_usage()

        # ensure category is valid
        category_input = argv.pop(0)
        (category_name, category_class) = self.find_category (category_input)
        if not category_name or not category_class:
            self.summary_usage(category_name)

        usage = "%%prog %s command [options]" % (category_name)
        parser = OptionParser(usage=usage)
        
        # ensure command is valid      
        category_instance = category_class()
        commands = category_instance._get_commands()
        if len(argv) < 1:
            # xxx what is this about ?
            command_name = '__call__'
        else:
            command_input = argv.pop(0)
            command_name = Candidates (commands).only_match (command_input)
    
        if command_name and hasattr(category_instance, command_name):
            command = getattr(category_instance, command_name)
        else:
            self.summary_usage(category_name)

        # ensure options are valid
        usage = "%%prog %s %s [options]" % (category_name, command_name)
        parser = OptionParser(usage=usage)
        for args, kwdargs in getattr(command, 'add_options', []):
            parser.add_option(*args, **kwdargs)
        (opts, cmd_args) = parser.parse_args(argv)
        cmd_kwds = vars(opts)

        # dont overrride meth
        for k, v in cmd_kwds.items():
            if v is None:
                del cmd_kwds[k]

        # execute command
        try:
            #print "invoking %s *=%s **=%s"%(command.__name__,cmd_args, cmd_kwds)
            command(*cmd_args, **cmd_kwds)
            sys.exit(0)
        except TypeError:
            print "Possible wrong number of arguments supplied"
            #import traceback
            #traceback.print_exc()
            print command.__doc__
            parser.print_help()
            sys.exit(1)
            #raise
        except Exception:
            print "Command failed, please check log for more info"
            raise
            sys.exit(1)

SfaAdmin().main()
