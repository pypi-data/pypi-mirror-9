import os
import sys
import imp
import pdb as pdb_module

from karmadbg.dbgcore.util import *

def help(vars):
    return "help meeeeeeeeeeeeeee!"

class PdbAutoDbg(object):

    def __enter__(self):
        self.origtrace = sys.gettrace()
        pdb_module.Pdb( skip=['*.stdmacro', 'dbgcore.*'] ).set_trace()
                
    def __exit__(self, type, value, traceback):
        sys.settrace(self.origtrace)


def pdb(vars):

    fileName = vars[0]
    args = vars[1:]

    argv = sys.argv
    __name__ = globals()["__name__"]
    __file__ =  globals()["__file__"]

    try:

        dirname, _ = os.path.split(fileName)

        if not dirname:
            script, suffix = os.path.splitext(fileName)
            _,fileName,desc=imp.find_module(script)

        globals()["__name__"] = "__main__"
        globals()["__file__"] = fileName

        sys.argv = []
        sys.argv.append(fileName)
        sys.argv.extend(args)

        
        with PdbAutoDbg() as dbg:
            execfile(fileName)

    except:
        sys.stderr.write(showtraceback( sys.exc_info(), 2 ))
        pass

    sys.argv = argv
    globals()["__name__"] = __name__
    globals()["__file__"] = __file__

def home(*args):
    import os.path
    homedir = os.path.expanduser("~")
    return os.path.join(homedir, ".karmadbg") 

def edit(vars):
    import os
    os.system("notepad %s" % " ".join(vars))
