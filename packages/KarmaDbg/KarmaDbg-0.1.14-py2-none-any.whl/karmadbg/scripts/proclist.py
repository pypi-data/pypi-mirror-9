import pykd

class ProcessesSnapshot(object):

    def __init__(self, currentProcess, currentThread, processList):
        self.currentProcessID = currentProcess
        self.currentThreadID = currentThread
        self.processList = processList

class ProcessInfo(object):
    
    def __init__(self, pid, exeName, threadList, breakpointList):
        self.pid = pid
        self.exeName = exeName
        self.threadList = threadList
        self.breakpointList = breakpointList

def getProcessThreadList():

    procLst = []

    currentProcess = pykd.targetProcess.getCurrent()
    currentThread =  currentProcess.currentThread()

    for procIndex in xrange(pykd.targetProcess.getNumber()):
        process = pykd.targetProcess.getProcess(procIndex)
        threadLst = []
        breakpointLst = []
        for threadIndex in xrange(process.getNumberThreads()):
            thread = process.thread(threadIndex)
            threadLst.append( (thread.systemID,) )
        #uncomment after pykd fixed
        #for bpIndex in xrange(process.getNumberBreakpoints()):
        #    bp = process.breakpoint(bpIndex)
        #    breakpointLst.append( bp.getOffset() )
        procLst.append( ProcessInfo(process.systemID, process.exeName, threadLst, breakpointLst) )

    return ProcessesSnapshot(currentProcess.systemID, currentThread.systemID, procLst )

def setCurrentThread(pid, tid):

    for procIndex in xrange(pykd.targetProcess.getNumber()):
        process = pykd.targetProcess.getProcess(procIndex)
        if process.systemID != pid:
            continue

        for threadIndex in xrange(process.getNumberThreads()):
            thread = process.thread(threadIndex)
            if thread.systemID == tid:
                thread.setCurrent()
                break
        return

