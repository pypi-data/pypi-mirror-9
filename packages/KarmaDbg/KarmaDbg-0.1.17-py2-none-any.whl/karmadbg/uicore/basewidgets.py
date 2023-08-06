from PySide.QtGui import *
from PySide.QtCore import *

from abc import abstractmethod

class BaseTextEdit(QPlainTextEdit):

    def getCurrentLineColor(self):
        return self.currentLineColor

    def setCurrentLineColor(self, val):
        self.currentLineColor = val

    current_line_color =  Property(str,getCurrentLineColor,setCurrentLineColor)

    def getCurrentLineBackground(self):
        return self.currentLineBackground

    def setCurrentLineBackground(self, val):
        self.currentLineBackground = val

    current_line_background =Property(str,getCurrentLineBackground,setCurrentLineBackground)

    def getBpLineColor(self):
        return self.bpLineColor

    def setBpLineColor(self,val):
        self.bpLineColor=val

    bp_line_color = Property(str,getBpLineColor, setBpLineColor)

    def getBpLineBackground(self):
        return self.getBpLineBackground

    def setBpLineBackground(self, val):
        self.bpLineBackground = val

    bp_line_background = Property(str,getBpLineBackground, setBpLineBackground)

    def __init__(self,parent=None):
        super(BaseTextEdit,self).__init__(parent)
        self.currentLineColor = 'black'
        self.currentLineBackground = 'white'
        self.bpLineColor = 'red'
        self.bpLineBackground = 'white'
        


class NativeDataViewWidget(QDockWidget):

    def __init__(self, uimanager):
        super(NativeDataViewWidget,self).__init__()
        self.uimanager = uimanager

        self.uimanager.targetRunning.connect(self.onTargetRunning)
        self.uimanager.targetStopped.connect(self.onTargetStopped)
        self.uimanager.targetDetached.connect(self.onTargetDetached)

        self.uimanager.targetThreadChanged.connect(self.onThreadChanged)
        self.uimanager.targetFrameChanged.connect(self.onFrameChanged)
        self.uimanager.targetBreakpointsChanged.connect(self.onBreakpointChanged)

    def constructDone(self):
        if self.widget():
            self.widget().setEnabled(False)

    def onTargetRunning(self):
        if self.widget():
            self.widget().setEnabled(False)

    def onTargetStopped(self):
        self.dataUpdate()
        if self.widget():
            self.widget().setEnabled(True)

    def onTargetDetached(self):
        self.dataUnavailable()
        if self.widget():
            self.widget().setEnabled(False)

    def onThreadChanged(self):
        self.dataUpdate()

    def onFrameChanged(self):
        self.dataUpdate()

    def onBreakpointChanged(self):
        self.dataUpdate()

    @abstractmethod
    def dataUnavailable(self):
        pass

    @abstractmethod
    def dataUpdate(self):
        pass

class PythonDataViewWidget(QDockWidget):
    def __init__(self, uimanager):
        super(PythonDataViewWidget, self).__init__()
        self.uimanager = uimanager
        self.uimanager.pythonRunning.connect(self.onPythonRunning)
        self.uimanager.pythonStopped.connect(self.onPythonStopped)
        self.uimanager.pythonExit.connect(self.onPythonExit)
        self.uimanager.pythonDataChanged.connect(self.onPythonDataChanged)

    def constructDone(self):
        if self.widget():
            self.widget().setEnabled(False)

    def onPythonRunning(self):
        if self.widget():
            self.widget().setEnabled(False)

    def onPythonStopped(self):
        self.dataUpdate()
        if self.widget():
            self.widget().setEnabled(True)

    def onPythonExit(self):
        self.dataUnavailable()
        if self.widget():
            self.widget().setEnabled(False)

    def onPythonDataChanged(self):
        self.dataUpdate()

    @abstractmethod
    def dataUnavailable(self):
        pass

    @abstractmethod
    def dataUpdate(self):
        pass

class AutoQMutex(QObject):

    def __init__(self,mutex):
        super(AutoQMutex,self).__init__()
        self.mutex=mutex

    def __enter__(self):
        return self.mutex

    def __exit__(self, type, value, tb):
        self.mutex.unlock()
