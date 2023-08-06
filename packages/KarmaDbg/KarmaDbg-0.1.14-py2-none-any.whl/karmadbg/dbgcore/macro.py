
import pkgutil
import sys
import imp
import os

def macroCommand(macroCmdLine):
    if len(macroCmdLine) > 0 and macroCmdLine[0] == '%':
        retval = runMacro(macroCmdLine)
        if retval != None:
            print retval
        return True
    return False

def runMacro(macroCmdLine):

    try:

        vars = macroCmdLine.split()

        if  vars[0][0] != '%':
            raise MacroError(r"macro name must begin with %")

        macro = getMacro( vars[0][1:] )

        ret = macro( vars[1:] )

        if not ret:
            ret = ''

        return ret

    except MacroError:
        sys.stderr.write( "MACRO ERROR: %s\n" % sys.exc_info()[1] )

class MacroError(Exception):

    def __init__(self, desc):
        self.desc = desc

    def __str__(self):
        return self.desc

def getMacro(macroName):

    import karmadbg
    dirname = os.path.dirname(karmadbg.__file__)

    _, macroPath, _ = imp.find_module('macros', [dirname])

    macroModules = [ name for _, name, _ in pkgutil.iter_modules([macroPath])]

    for macroModuleName in macroModules:

        try:

             macroModule = __import__( 'karmadbg.macros.' + macroModuleName, fromlist=['*'] )

             if macroName in dir(macroModule):
                return macroModule.__dict__[macroName]
        except ImportWarning:

            pass

    raise MacroError("failed to find macro")
