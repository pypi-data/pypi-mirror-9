"""completing.py  done action module

"""
#print("module {0}".format(__name__))


import time
import struct
from collections import deque
import inspect


from .globaling import *
from .odicting import odict
from . import aiding
from . import excepting
from . import registering
from . import storing
from . import acting
from . import tasking
from . import framing

from .consoling import getConsole
console = getConsole()

class Complete(acting.Actor):
    """Complete Class for indicating tasker done state

    """
    Registry = odict()

    def _resolve(self, taskers, **kwa):
        """Resolves value (taskers) list of link names that is passed in as parm
           resolved links are passed back to ._act to store in parms
        """
        parms = super(Complete, self)._resolve( **kwa)

        links = set()
        for tasker in taskers:
            if tasker == 'me':
                tasker = self._act.frame.framer
                links.add(tasker)

            else:
                tasker = tasking.resolveTasker(tasker,
                                               who=self.name,
                                               desc='tasker',
                                               contexts=[AUX, SLAVE],
                                               human=self._act.human,
                                               count=self._act.count)
                links.add(tasker)

        parms['taskers'] = links #replace with valid list
        return parms

class CompleteDone(Complete):
    """CompleteDone Complete

    """
    def action(self, taskers, **kw):
        """set done state to True for aux or slave framer

        """
        for tasker in taskers:
            tasker.done = True
            console.profuse("    Done {0}\n".format(tasker.name))

        return None
