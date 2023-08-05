
import sys

from pprint import pprint
from bdb import Bdb, BdbQuit

from karmadbg.dbgcore.dbgdecl import *
from karmadbg.dbgcore.util import *

class PythonDebugger(Bdb):

    def __init__(self, debugServer):
        Bdb.__init__(self, skip=["karmadbg.dbgcore.*"])
        self.eventHandler = debugServer.getClientEventHandler()
        self.debugServer = debugServer
        self.origtrace = None

    def __enter__(self):
        self.origtrace = sys.gettrace()
        self.topframe = sys._getframe().f_back
        self.set_trace()

    def __exit__(self, type, value, traceback):
        sys.settrace(self.origtrace)
        self.eventHandler.onPythonQuit()

    def execfile(self, fileName, globals, locals):
        self.needQuit = False
        if self.eventHandler.onPythonStart(self.canonic(fileName)):
            with self:
                try:
                    execfile(fileName, globals, locals)
                except BdbQuit:
                    pass

    def execcode(self, code, globals, locals):
        self.needQuit = False
        if self.eventHandler.onPythonStart("<string>"):
            with self:
                try:
                    exec code in globals, locals
                except BdbQuit:
                    pass

    def user_line(self, frame):
        self.currentFrame = frame
        self.eventHandler.onPythonStateChanged(TargetState(TargetState.TARGET_STOPPED))
        self.interract(frame)
        self.eventHandler.onPythonStateChanged(TargetState(TargetState.TARGET_RUNNING))


    def user_exception(self, frame, exc_info):

        self.currentFrame = frame

        print "!!! Exception"
        print showexception(exc_info)

        self.eventHandler.onPythonStateChanged(TargetState(TargetState.TARGET_STOPPED))
        self.interract(frame)
        self.eventHandler.onPythonStateChanged(TargetState(TargetState.TARGET_RUNNING))


    def interract(self, frame):
        self.debugServer.commandServer.sendAnswer( MakeResultOk() )
        if self.debugServer.commandLoop(self):
            raise BdbQuit
        if self.needQuit == True:
            raise BdbQuit


    def debugCommand(self, commandStr, echo=False):

        tokens = commandStr.split()

        if len(tokens) == 0:
            self.debugServer.commandServer.sendAnswer( MakeResultOk() )
            return False

        if tokens[0] == 'q':
            print "stop python debugger"
            self.needQuit = True
            return True

        if tokens[0] == 'g':
            self._set_stopinfo(self.botframe, None, -1)
            return True

        if tokens[0] == 't':
            self.set_step()
            return True

        if tokens[0] == 'p':
            self.set_next(self.currentFrame)
            return True

        if tokens[0] == 'bp':
            try:
                if len(tokens) < 2:
                    self.setPythonBreakpoint( self.canonic( self.currentFrame.f_code.co_filename), self.currentFrame.f_lineno)
                if len(tokens) < 3:
                    self.setPythonBreakpoint( self.canonic( self.currentFrame.f_code.co_filename), int(tokens[1]))
                else:
                    self.setPythonBreakpoint(tokens[1], int(tokens[2]))
            except:
                print "failed to set breakpoint"

            self.debugServer.commandServer.sendAnswer( MakeResultOk() )
            
            return False

        if tokens[0] == 'bc':
            try:
                if len(tokens) < 2:
                    self.removePythonBreakpoint( self.canonic( self.currentFrame.f_code.co_filename), self.currentFrame.f_lineno)
                if len(tokens) < 3:
                    self.removePythonBreakpoint( self.canonic( self.currentFrame.f_code.co_filename), int(tokens[1]))
                else:
                    self.removePythonBreakpoint(tokens[1], int(tokens[2]))
            except:
                print "failed to remove breakpoint"

            self.debugServer.commandServer.sendAnswer( MakeResultOk() )
            
            return False

        if tokens[0] == 'pp':
            try:
                pprint( eval(tokens[1], self.currentFrame.f_globals, self.currentFrame.f_locals), sys.stdout)
            except:
                print showexception(sys.exc_info()) 
            self.debugServer.commandServer.sendAnswer( MakeResultOk() )
            
            return False

        if tokens[0] == 'w':
            for l in self.getPythonStackTrace():
                print "%s\t%s : %d" % l

            self.debugServer.commandServer.sendAnswer( MakeResultOk() )
           
            return False

        if tokens[0] == 'h':
            print "Commands:"
            print  "q - quit from debugger"
            print  "g - go "
            print  "t - trace in"
            print  "p - step over"
            print  "bp [file] lineno - set breakpoint"
            print  "bc [file] lineno - remove breakpoint"
            print  "w - print stack"
            print  "pp var - print variable"
            print  "h - read this"

            self.debugServer.commandServer.sendAnswer( MakeResultOk() )
           
            return False

        print "invalid command"
        self.debugServer.commandServer.sendAnswer( MakeResultOk() )
        return False
    
    def getPythonSourceLine(self):
       fileName = self.canonic( self.currentFrame.f_code.co_filename)
       fileLine = self.currentFrame.f_lineno
       return (fileName, fileLine)

    def getPythonStackTrace(self):
        stack = []
        frame = self.currentFrame
        while frame is not None and frame is not self.topframe:
            stack.append((frame.f_code.co_name, frame.f_globals["__name__"], frame.f_lineno))
            frame = frame.f_back
        return stack

    def setPythonBreakpoint(self, fileName, lineno):
        self.set_break(self.canonic(fileName), lineno)
        self.eventHandler.onPythonBreakpointAdd(self.canonic(fileName),lineno)

    def removePythonBreakpoint(self, fileName, lineno):
        self.clear_break(self.canonic(fileName), lineno)
        self.eventHandler.onPythonBreakpointRemove(self.canonic(fileName),lineno)

    def getPythonBreakpointList(self):
        return self.get_all_breaks()

    def getPythonLocals(self, localNames):
        
        def getVars(vars,names):
            if len(names) == 0:
                return [ (name, str(val) ) for name, val in vars.items()]
            else:
                if names[0] in vars and hasattr(vars[names[0]], "__dict__"):
                    return getVars( vars[names[0]].__dict__, names[1:] )
            return []

        return getVars(self.currentFrame.f_locals,localNames)


