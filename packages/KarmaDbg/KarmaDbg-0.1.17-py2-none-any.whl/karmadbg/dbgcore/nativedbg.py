from codeop import compile_command

import pykd
from pykd import *

from karmadbg.dbgcore.dbgdecl import *
from karmadbg.dbgcore.util import *
from karmadbg.dbgcore.pydebug import PythonDebugger

class EventMonitor(pykd.eventHandler):

    def __init__(self, debugServer):
        super(EventMonitor,self).__init__()
        self.eventHandler = debugServer.eventHandler
        self.debugServer = debugServer

    def onExecutionStatusChange(self, status):
        event = { 
            pykd.executionStatus.Go : TargetState(TargetState.TARGET_RUNNING),
            pykd.executionStatus.Break : TargetState(TargetState.TARGET_STOPPED),
            pykd.executionStatus.NoDebuggee : TargetState(TargetState.TARGET_DETACHED)
        }[status]

        if event.IsStopped:
            self.debugServer.frame = pykd.getFrame()

        self.eventHandler.onTargetStateChanged(event)

    def onCurrentThreadChange(self, threadId):
        self.debugServer.frame = pykd.getFrame()
        self.eventHandler.onTargetChangeCurrentThread()

    def onChangeLocalScope(self):
        frame = pykd.getFrame()
        self.debugServer.frame = frame
        self.eventHandler.onTargetChangeCurrentFrame( (frame.ip, frame.ret, frame.fp, frame.sp) )

    def onChangeBreakpoints(self):
        self.eventHandler.onTargetChangeBreakpoints()

    def onDebugOutput(self, text):
        sys.stdout.write(text)
    
class NativeDebugger(object):

    def __init__(self, debugServer):
        self.eventHandler = debugServer.getClientEventHandler()
        self.clientOutput = debugServer.getClientOutput()
        self.debugServer = debugServer
        self.stepSourceMode = False

        pykd.initialize()

        self.eventMonitor = EventMonitor(self)

       
    def isNativeCmd(self, commandStr):
        return commandStr in ['g', 'p', 't', 'gu']

    def nativeCmd(self,commandStr):
        try:
            res = { 
                'g' : self.targetGo,
                'p' : self.targetStep,
                't' : self.targetTrace,
                'gu' : pykd.stepout,
            }[commandStr]()
            if res:
                print res
            return MakeResultOk()
        except pykd.DbgException:
            print showexception(sys.exc_info())
            return MakeResultError()

    def targetGo(self):
        return pykd.go()

    def targetStep(self):
        if self.stepSourceMode == True:
            return pykd.sourceStepOver()
        return pykd.step()

    def targetTrace(self):
        if self.stepSourceMode == True:
            return pykd.sourceStep()
        return pykd.trace()


    def isWindbgCommand(self, commandStr):
        return commandStr[0] in ['.', '!', '~', '?', '#', '|', ';', '$']

    def windbgCommand(self, commandStr):
        try:
            pykd.dbgCommand(commandStr, suppressOutput=False)
            #res = pykd.dbgCommand(commandStr, suppressOutput=False)
            #if res:
            #    print res
            return MakeResultOk()
        except pykd.DbgException:
            print showtraceback(sys.exc_info())
            return MakeResultError()

    def getSourceLine(self):
        try:
            ip = self.frame.ip
            fileName, fileLine, displacement = pykd.getSourceLine(ip)
            return (fileName, fileLine)
        except pykd.DbgException:
            return ("", 0)

    def getDisasm(self,relpos,linecount):
        ip = self.frame.ip
        try:
            for i in xrange(linecount):
                dasm = pykd.disasm(ip)
                dasm.jumprel(relpos + i)
                dasmLines.append(dasm.instruction())
            return dasmLines
        except pykd.DbgException:
            return []

    def getRegsiters(self):
        return [ r for r in cpu() ]

    def getStackTrace(self):
        try:
            stack = pykd.getStack()
            return [ (frame.frameOffset, frame.returnOffset, pykd.findSymbol(frame.instructionOffset, True) ) for frame in stack ]
        except pykd.DbgException:
            return []

    def setCurrentFrame(self, frameNo):
        try:
            pykd.setFrame(frameNo)
        except pykd.DbgException:
            pass

    def getCurrentFrame(self):
        return ( self.frame.ip, self.frame.ret, self.frame.fp, self.frame.sp )

    def getExpr(self,expr):
        try:
            return pykd.expr(expr)
        except pykd.DbgException:
            pass

    def pythonEval(self, expr):
        try:
            return str( eval(expr) )
        except Exception, e:
            return str(e)

    def getMemoryRange(self,addr,length):
        try:
            return pykd.loadBytes(pykd.addr64(addr),length)
        except pykd.MemoryException:
            return None

    def breakin(self):
        try:
            pykd.breakin()
        except pykd.DbgException:
            pass

    def setStepSourceMode(self, mode):
        self.stepSourceMode = mode
