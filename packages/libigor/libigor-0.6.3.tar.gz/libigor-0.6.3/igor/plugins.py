# -*- coding: utf-8 -*-
from collections import namedtuple as ntuple
import pkgutil
import logging


StrategyRunner  = ntuple('StrategyRunner', 'name run')
PluginDesc      = ntuple('PluginDesc', 'type name run')


#==============================================================================
class PluginManager(object):
    #------------------------------------------------------------------------//
    def __init__(self, plugDir):
        self.plugDir    = plugDir
        self.snipers    = {}
        self.collectors = {}
        self.plugins    = {}

    #------------------------------------------------------------------------//
    def register(self, plugtype, name):
        logging.info("DEFINE PLUGIN {0} - {1}".format(plugtype, name))

        def decorate(func):
            logging.info("ADD_PLUGIN {0} - {1}".format(plugtype, name))
            plugset         = self.plugins.setdefault(plugtype, {})
            plugset[name]   = func
            return func
        return decorate

    #------------------------------------------------------------------------//
    def bytype(self, plugtype):
        plugset = self.plugins.get(plugtype)
        if plugset:
            return (PluginDesc(plugtype, *s) for s in plugset.items())
        return []

    #------------------------------------------------------------------------//
    def iter(self):
        for plugtype, plugset in self.plugins.items():
            for name, runfn in plugset.items():
                yield PluginDesc(plugtype, name, runfn)

    #------------------------------------------------------------------------//
    def find(self, plugtype, name):
        plugset = self.plugins.get(plugtype)
        if plugset:
            runfn = plugset.get(name)
            if runfn:
                return PluginDesc(plugtype, name, runfn)
        logging.warning("Existing plugins {}".format(', '.join(plugset.keys())))
        return None

    #------------------------------------------------------------------------//
    def discover(self):
        for imp, name, ispkg in pkgutil.walk_packages([self.plugDir]):
            mod = imp.find_module(name)
            logging.debug("Loading plugin {}.py".format(name))
            try:
                #__import__(fullName)
                mod.load_module(name)
            except ImportError:
                logging.error("Failed to import plugin '{}'".format(name))
                from traceback import format_exc; logging.error(format_exc())


#----------------------------------------------------------------------------//
def syncplugins(plugmgr, existing, createfn, deletefn):
    """
    Helper function for syncing plugins. Backend agnostic - all backend
    functionality is passed through ``deletefn`` and ``createfn``

    plugmgr     - Plugin manager used
    existing    - A list of existing plugins. Each item needs to have ``type``,
                  ``name``, and ``run`` attributes.
    deletefn    - Deletion function. This will be called when the plugin should
                  be deleted. It takes one argument - the deleted plugin. This
                  will be an item from the ``existing`` list.
    createfn    - Function used to create new plugin. It should take one
                  argument - ``PluginDesc`` with description of the new plugin.
    """
    plugmgr.discover()
    newsnipers  = list(plugmgr.iter())

    for plugin in existing:
        if plugmgr.find(plugin.type, plugin.name):
            # Still exists
            plug_eq = lambda x: x.type != plugin.type or x.name != plugin.name
            newsnipers = filter(plug_eq, newsnipers)
        else:
            # removed
            deletefn(plugin)

    for sniper in newsnipers:
        createfn(sniper)
