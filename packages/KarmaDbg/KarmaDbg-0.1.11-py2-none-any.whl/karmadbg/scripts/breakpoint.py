import pykd

def getBreakpoints():
    bpNumber = pykd.getNumberBreakpoints()
    return [ pykd.getBp(bpIndex).getOffset() for bpIndex in xrange(bpNumber) ]

def removeBreakpoint(offset):
    for i in xrange( pykd.getNumberBreakpoints() ):
        bp = pykd.getBp(i)
        if bp.getOffset() == offset:
            bp.remove()
            return

def setBreakpoint(offset):
    pykd.setBp(offset)
