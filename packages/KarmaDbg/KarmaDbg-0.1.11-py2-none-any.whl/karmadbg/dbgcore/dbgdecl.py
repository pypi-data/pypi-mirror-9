

from abc import abstractmethod

class DebugCommandResult(object):

    '''
    Debug command result
    '''

    OK = 0
    ERROR = 1
    NEEDMOREDATA = 2
    QUIT = 3
    
    def __init__(self,res):
        self.res=res

    @property
    def IsOK(self):
        return self.res == self.OK

    @property
    def IsError(self):
        return self.res == self.ERROR

    @property
    def IsNeedMoreData(self):
        return self.res == self.NEEDMOREDATA

    @property
    def IsQuit(self):
        return self.res == self.QUIT


def MakeResultOk():
    return DebugCommandResult(DebugCommandResult.OK)

def MakeResultError():
    return DebugCommandResult(DebugCommandResult.ERROR)

def MakeResultNeedMoreData():
    return DebugCommandResult(DebugCommandResult.NEEDMOREDATA)

def MakeResultQuit():
    return DebugCommandResult(DebugCommandResult.QUIT)



class TargetState(object):

    '''
    Target state
    '''

    TARGET_RUNNING = 0
    TARGET_STOPPED = 1
    TARGET_DETACHED = 2

    def __init__(self,state):
        super(TargetState,self).__init__()
        self.state = state

    @property
    def IsRunning(self):
        return self.state == TargetState.TARGET_RUNNING

    @property
    def IsStopped(self):
        return self.state == TargetState.TARGET_STOPPED

    @property
    def IsNoTarget(self):
        return self.state == TargetState.TARGET_DETACHED


class AbstractDebugClient(object):

    '''
    Abstarct interface for debug client
    '''

    @abstractmethod
    def output(self,str):
        pass

    @abstractmethod
    def input(self):
        pass

    @abstractmethod
    def onTargetStateChanged(self,state):
        pass

    @abstractmethod
    def onTargetChangeCurrentThread(self):
        pass

    @abstractmethod
    def onTargetChangeCurrentFrame(self, frame):
        pass

    @abstractmethod
    def onTargetChangeBreakpoints(self):
        pass

    @abstractmethod
    def onPythonStart(self):
        return False
    
    @abstractmethod
    def onPythonQuit(self):
        pass

    @abstractmethod
    def onPythonStateChange(self,state):
        pass
    
    @abstractmethod
    def onPythonBreakpointAdd(self, file, line):
        pass

    @abstractmethod
    def onPythonBreakpointRemove(self, file, line):
        pass
