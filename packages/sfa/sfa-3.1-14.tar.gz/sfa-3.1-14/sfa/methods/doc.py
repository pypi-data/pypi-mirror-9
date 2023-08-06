#!/usr/bin/env python
# todo this should inspect the generic flavour
import sfa.methods
from sfa.managers.registry_manager import RegistryManager
from sfa.managers.aggregate_manager import AggregateManager
from sfa.managers.slice_manager import SliceManager

managers_map={'registry': RegistryManager,
              'aggregate': AggregateManager,
              'slicemgr': SliceManager,
              }

for methodname in sfa.methods.all:
    module_path="sfa.methods.%s"%methodname
    classname=methodname
    try:
        module = __import__ (module_path, globals(), locals(), [classname])
        classobj=getattr(module, classname)
        print '----------',methodname
        if hasattr(classobj,__doc__):
            print classobj.__doc__
        for interface in classobj.interfaces:
            if interface=='component': continue
            print '   interface',interface,
            manager=managers_map[interface]
            if hasattr (manager, methodname): print 'OK'
            else: print 'MISSING ********************'
    except Exception,e:
        print "Something wrong with method %s (%s)"%(methodname,e)
