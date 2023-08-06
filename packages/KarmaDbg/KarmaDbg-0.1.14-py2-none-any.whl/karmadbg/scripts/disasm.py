
import pykd

def getDisasm(linecount, relpos = 0, offset = 0):
    dasmLines = []
    try:
        if offset == 0:
            offset = pykd.cpu().ip

        dasm = pykd.disasm(pykd.addr64(offset))
        dasm.jumprel(relpos)

        for i in xrange(linecount):

            symbol = None
            fileName = None
            lineNo = 0

            try:
                moduleName, symbol, displacement = pykd.findSymbolAndDisp(dasm.current())
                if displacement != 0:
                    symbol = None
                else:
                    symbol = "%s!%s" % ( moduleName, symbol)
            except pykd.DbgException:
                pass

            try:
                fileName, lineNo, displacement = pykd.getSourceLine(dasm.current())
                if displacement != 0:
                    fileName = None
                    lineNo = 0
            except pykd.DbgException:
                pass

            dasmLines.append(( dasm.current(), dasm.instruction(), symbol, fileName, lineNo,))

            dasm.disasm()

        return dasmLines

    except pykd.DbgException:
        return []
