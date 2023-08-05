# -*- coding: utf-8 -*-

"""
testing.py unit test module support classes and functions
"""
#print("module {0}".format(__name__))


import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os
import importlib

from ..base.consoling import getConsole
console = getConsole()

from ..base.odicting import odict

from ..base import globaling
from ..base import storing
from ..base import housing
from ..base import framing
from ..base import acting
from ..base import deeding



from .. import __version__

if sys.platform == 'win32':
    TEMPDIR = 'c:/temp'
    if not os.path.exists(TEMPDIR):
        os.mkdir(TEMPDIR)
else:
    TEMPDIR = '/tmp'


BEHAVIORS = []  # list of behavior package name strings

def setUpModule():
    console.reinit(verbosity=console.Wordage.concise)

    if BEHAVIORS:  # import behavior package/module given by BEHAVIORS
        for behavior in BEHAVIORS:
            mod = importlib.import_module(behavior)

def tearDownModule():
    pass

def initPathToData(store, path, data):
    """
    Returns share at path in store after creating and assigning data items
    to fields in share
    """
    share = store.create(path)
    verifyShareFields(share, data.keys())

    share.update(data)
    return share

def verifyShareFields(share, fields):
    """
    Verifies that updating fields in share won't violate the
       condition that when a share has field == 'value'
       it will be the only field

       share is  Share
       fields is list of field names


       raises ValueError exception if condition would be violated
    """
    if (len(fields) > 1) and ('value' in fields):
        raise ValueError("Invalid field named 'value' in {0}".format(fields))

    if share:  # does share have fields already
        for field in fields:
            if field not in share: #so this field could be added to share
                if ('value' in share) or (field == 'value'):
                    raise ValueError("Candidate field '{0}' when fields ="
                                     " '{1}' exist".format(field, share.keys()))


class IofloTestCase(unittest.TestCase):
    """
    Base TestCase for Ioflo TestCases
    """

    def setUp(self, behaviors=None):
        if behaviors:
            if self.behaviors: #import behavior package/module
                for behavior in self.behaviors:
                    mod = importlib.import_module(behavior)
        housing.House.Clear() #clear house registry
        housing.ClearRegistries() #clear all the other registries

    def tearDown(self):
        housing.House.Clear() #clear house registry
        housing.ClearRegistries() #clear all the other registries


class StoreIofloTestCase(IofloTestCase):
    """
    TestCase with only .store and .timer
    """

    def setUp(self):
        super(StoreIofloTestCase, self).setUp()

        self.store = storing.Store(stamp=0.0)

    def tearDown(self):
        super(StoreIofloTestCase, self).tearDown()

class HouseIofloTestCase(IofloTestCase):
    """
    TestCase with  .house and .store from .house
    """

    def setUp(self):
        super(HouseIofloTestCase, self).setUp()

        self.house = housing.House(name = "HouseTest")
        self.store = self.house.store
        self.house.assignRegistries()
        self.metas = [
                ("name", "meta.name", odict(value="Tester")),
                ("period", "meta.period", odict(value=0.125)),
                ("real", "meta.real", odict(value=False)),
                ("mode", "meta.mode", odict(value=None)),  # applied mode logging only
                ("plan", "meta.plan", odict(value="Test.flo")),
                ("filepath", "meta.filepath", odict(value="")),
                ("behaviors", "meta.behaviors", odict(value=BEHAVIORS)),
                ("credentials", "meta.credentials",
                 odict([('username', "Testee"), ('password', "Password")])),
                ("failure", "meta.failure", odict(value="")),  # for failure reporting
                ("framers", "meta.framers", odict()),  # for failure reporting
                ("taskables", "meta.taskables", odict(value=set())),  # to add taskables at runtime
            ]
        self.setupMetas()
        self.preloads = [
                ("ioflo.version", odict(value=__version__)),
                ("ioflo.platform",
                        odict([("os", sys.platform),
                        ("python", "{0}.{1}.{2}".format(*sys.version_info)),] )),
            ]
        self.setupPreloads()


    def tearDown(self):
        super(HouseIofloTestCase, self).tearDown()

    def setupMetas(self, extras=None):
        """
        Create and add meta shares to house and store
        add the extras to the default metas

        extras is a list of triples of the form (key, path, odict()
        """
        if extras:
            self.metas.extend(extras)

        for name, path, data in self.metas:
            self.house.metas[name] = initPathToData(self.store, path, data)

        self.house.metas['house'] = initPathToData(self.store,
                                                   '.meta.house',
                                                   odict(value=self.house.name))

    def setupPreloads(self, extras=None):
        """
        Create and add preload shares to store
        add the extras to the default preloads
        extras  is a list of duples of the form (path, odict())
        """
        if extras:
            self.preloads.extend(extras)

        for path, data in self.preloads:
            initPathToData(self.store, path, data)

    def resolve(self):
        """
        Resolve the house
        """
        self.house.resolve()


class FramerIofloTestCase(HouseIofloTestCase):
    """
    TestCase with .framer in .house and .store from .house
    """

    def setUp(self):
        super(FramerIofloTestCase, self).setUp()
        self.framer = framing.Framer(name="FramerTest",
                                     store=self.store)
        self.house.taskers.append(self.framer)
        self.house.framers.append(self.framer)
        self.house.mids.append(self.framer)
        self.house.orderTaskables()
        self.framer.assignFrameRegistry()

    def tearDown(self):
        super(FramerIofloTestCase, self).tearDown()

class FrameIofloTestCase(FramerIofloTestCase):
    """
    TestCase with .frame in .framer in .house and .store from .house
    """

    def setUp(self):
        super(FrameIofloTestCase, self).setUp()
        self.frame = framing.Frame(name="FrameTest",
                                  store=self.store,
                                  framer=self.framer)
        self.framer.first = self.frame

    def tearDown(self):
        super(FrameIofloTestCase, self).tearDown()

    def addDeed(self,
                kind,
                context=globaling.RECUR,
                inits=None,
                ioinits=None,
                parms=None,
                prerefs=None ):
        """
        Create act to run deed class name given by kind and
        add to context.
        """
        act = acting.Act(actor=kind,
                         registrar=deeding.Deed,
                         inits=inits,
                         ioinits=ioinits,
                         parms=parms,
                         prerefs=prerefs)

        if context == globaling.NATIVE:
            context = globaling.RECUR

        self.frame.addByContext(act, context)
        return act

    def addBenterDeed(self, kind, **kwa):
        """
        Create Act with actor of kind and add deed at BENTER context
        """
        return self.addDeed(kind, context=globaling.BENTER, **kwa)

    def addEnterDeed(self, kind, **kwa):
        """
        Create Act with actor of kind and add deed at ENTER context
        """
        return self.addDeed(kind, context=globaling.ENTER, **kwa)

    def addRenterDeed(self, kind, **kwa):
        """
        Create Act with actor of kind and add deed at RENTER context
        """
        return self.addDeed(kind, context=globaling.RENTER, **kwa)

    def addRecurDeed(self, kind, **kwa):
        """
        Create Act with actor of kind and add deed at RECUR context
        """
        return self.addDeed(kind, context=globaling.RECUR, **kwa)

    def addPrecurDeed(self, kind, **kwa):
        """
        Create Act with actor of kind and add deed at PRECUR context
        """
        return self.addDeed(kind, context=globaling.PRECUR, **kwa)

    def addExitDeed(self, kind, **kwa):
        """
        Create Act with actor of kind and add deed at EXIT context
        """
        return self.addDeed(kind, context=globaling.EXIT, **kwa)

    def addRexitDeed(self, kind, **kwa):
        """
        Create Act with actor of kind and add deed at REXIT context
        """
        return self.addDeed(kind, context=globaling.REXIT, **kwa)




