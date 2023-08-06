from karmadbg.dbgcore.varprint import *
import pykd


@shortprinter(r"Char\*", r"Char\[\d+\]")
def charShortPrinter(var):
    try:
        str = pykd.loadCStr(var)
        str = str if len(str) < 32 else str[0:32] + "..."
        return "\"%s\" (0x%x)"  % (str,var)
    except:
        pass

@shortprinter(r"WChar\*", r"WChar\[\d+\]")
def charShortPrinter(var):
    try:
        str = pykd.loadWStr(var)
        str = str if len(str) < 32 else str[0:32] + "..."
        return "\"%s\" (0x%x)"  % (str,var)
    except:
        pass
