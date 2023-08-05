
import pykd

def getDisasm(linecount, relpos = 0, offset = 0):
    dasmLines = []
    try:
        if offset == 0:
            offset = pykd.cpu().ip
        for i in xrange(linecount):
            dasm = pykd.disasm(pykd.addr64(offset))
            dasm.jumprel(relpos + i)
            dasmLines.append(( dasm.current(), dasm.instruction() ))
        return dasmLines
    except pykd.DbgException:
        return []
