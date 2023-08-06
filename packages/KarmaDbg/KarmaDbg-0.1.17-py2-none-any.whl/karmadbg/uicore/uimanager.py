
import sys
import os

from itertools import ifilter

from PySide.QtCore import *
from PySide.QtGui import QMainWindow, QFileDialog, QAction, QKeySequence, QShortcut

from karmadbg.dbgcore.settings import DbgSettings
from karmadbg.uicore.dbgclient import DebugClient, DebugAsyncCall
from karmadbg.uicore.defaultstyle import defaultStyle, defaultCss

class UIManager(QObject):

    outputRequired = Signal(str)
    inputRequired = Signal()
    inputCompleted = Signal()
    showSourceRequired = Signal(str)

    targetRunning = Signal()
    targetStopped = Signal()
    targetDetached = Signal()
    targetThreadChanged = Signal()
    targetFrameChanged = Signal()
    targetBreakpointsChanged = Signal()

    pythonStarted = Signal(str)
    pythonRunning = Signal()
    pythonStopped = Signal()
    pythonExit = Signal()
    pythonDataChanged = Signal()
    pythonBreakpointAdded = Signal(str,int)
    pythonBreakpointRemoved = Signal(str,int)

    def __init__(self, app):
        super(UIManager,self).__init__()

        self.app = app
        self.app.focusChanged.connect(self.onFocusChanged)\

        import karmadbg
        projdir =  os.path.dirname(karmadbg.__file__)
        defaultSettingFile =  os.path.join( projdir, "settings", "default.xml")

        homedir = os.path.join( os.path.expanduser("~"), ".karmadbg")
        userSettingsFile = os.path.join( homedir, "default.xml" )

        self.dbgSettings = DbgSettings()
        self.dbgSettings.loadSettings(defaultSettingFile)
        self.dbgSettings.loadSettings(userSettingsFile, policy='overwrite')

        self.mainwnd = MainForm(self.dbgSettings.mainWindow)

        self.app.setStyleSheet(defaultStyle)
        if self.dbgSettings.style:
            if self.dbgSettings.style.fileName:
                if os.path.isabs(self.dbgSettings.style.fileName):
                    fileName = self.dbgSettings.style.fileName
                else:
                    filename = r"file:///" + os.path.join( projdir, self.dbgSettings.style.fileName )
                self.app.setStyleSheet(filename);

        self.docCss = defaultCss
        try:
            if self.dbgSettings.doccss:
                if self.dbgSettings.doccss.fileName:
                    if os.path.isabs(self.dbgSettings.doccss.fileName):
                        fileName = self.dbgSettings.doccss.fileName
                    else:
                        filename = os.path.join( projdir, self.dbgSettings.doccss.fileName )
                    with open(filename) as cssfile:
                        self.docCss = reduce( lambda x,y: x + y, cssfile)
        except:
            pass

        self.actions = ActionManager(self.dbgSettings, self)
        self.widgets = WidgetManager(self.dbgSettings, self)
        self.dialogs = DialogManager(self.dbgSettings, self)
        
        self.debugClient = DebugClient(self, self.dbgSettings)
        self.debugClient.start()

        self.mainMenu = getMainMenuManager(self.dbgSettings.mainMenu, self)

        self.app.aboutToQuit.connect(self.onQuit)
        self.mainwnd.show()

        print "KarmaDbg UI client. Version %s" % karmadbg.__version__ 
        print "load config from ", userSettingsFile

    def onQuit(self):
        self.debugClient.stop()

    def onFocusChanged(self, oldWidget, newWidget):
        findAction = self.getAction("FindAction")
        if findAction:
            findAction.setEnabled(hasattr(newWidget,"find"))

    def quit(self):
        self.mainwnd.close()

    def find(self, text, fromBegin = True):
        self.findTarget.find(text, fromBegin)

    def openProcess(self):
        if "OpenProcess" in self.dialogs:
            processName = self.getDialog("OpenProcess").getProcessName()
        else:
            processName = QFileDialog().getOpenFileName()[0]

        if processName:
            self.debugClient.openProcess(processName)

    def openDump(self):
        if "OpenDump" in self.dialogs:
            fileName = self.getDialog("OpenDump").getFileName()
        else:
            fileName = QFileDialog().getOpenFileName()[0]

        if fileName:
            self.debugClient.openDump(fileName)

    def openSource(self):
        if "OpenSource" in self.dialogs:
            fileName = self.getDialog("OpenSource").getFileName()
        else:
            fileName = QFileDialog().getOpenFileName()[0]

        if fileName:
            self.showSourceRequired.emit(fileName)


    def inputComplete(self,str):
        self.debugClient.inputCompleted.emit(str)

    def getWidget(self, name):
        if name in self.widgets:
            return self.widgets[name]

    def getDialog(self, name):
        if name in self.dialogs:
            return self.dialogs[name](self.dbgSettings,self)

    def getAction(self,name):
        if name in self.actions:
            return self.actions[name]

    def toggleWidget(self, name):
        widget = self.getWidget(name)
        if widget:
            widget.setVisible( widget.isVisible() == False )

    def showDialogModal(self,name):
        self.findTarget = self.app.focusWidget()
        dlg = self.getDialog(name)
        if dlg: dlg.exec_()

class MainForm(QMainWindow):

    def __init__(self, settings):
        super(MainForm,self).__init__(None)

        self.resize(settings.width, settings.height)
        self.setWindowTitle(settings.title)
        self.setDockNestingEnabled(True)


def getMainMenuManager(dbgsettings,uimanager):
    module = __import__( dbgsettings.module, fromlist=[dbgsettings.className])
    classobj = getattr(module, dbgsettings.className)
    return classobj(dbgsettings, uimanager)

class WidgetManager(QObject):

    def __init__(self, dbgsettings, uimanager):
        
        super(WidgetManager,self).__init__()

        self.uimanager = uimanager
        self.widgets = {}

        for widgetSetting in dbgsettings.widgets:
            self.widgets[ widgetSetting.name ] = self.constructWidget(widgetSetting)

    def constructWidget(self, widgetSettings):
        module = __import__( widgetSettings.module, fromlist=[widgetSettings.className])
        classobj = getattr(module, widgetSettings.className)
        obj = classobj(widgetSettings, self.uimanager)
        obj.behaviour = widgetSettings.behaviour
        obj.setVisible(widgetSettings.visible)
        if hasattr(obj, "constructDone"): obj.constructDone()
        if widgetSettings.title:
            obj.setWindowTitle(widgetSettings.title)
        return obj

    def __getitem__(self,name):
        return self.widgets[name]

    def __contains__(self,name):
        return name in self.widgets

    def values(self):
        return self.widgets.values()


class DialogManager(QObject):

    def __init__(self, dbgsettings, uimanager):
        
        super(DialogManager,self).__init__()

        self.uimanager = uimanager
        self.dialogs = {}

        for dialogSetting in dbgsettings.dialogs:
            self.dialogs[ dialogSetting.name ] = self.constructDialog(dialogSetting)

    def constructDialog(self, dialogSetting):
        module = __import__( dialogSetting.module, fromlist=[dialogSetting.className])
        classobj = getattr(module, dialogSetting.className)
        return classobj

    def __getitem__(self,name):
        return self.dialogs[name]

    def __contains__(self,name):
        return name in self.dialogs

class ActionManager(QObject):

    def __init__(self,dbgsettings, uimanager):
        super(ActionManager, self).__init__()
        self.uimanager = uimanager
        self.actions = {}

        for actionSetting in dbgsettings.actions:
            self.actions[ actionSetting.name ] = self.constructAction(actionSetting)

    def __getitem__(self,name):
        if name in self.actions:
            return self.actions[name]
        return QAction(name,self.uimanager.mainwnd)

    def __contains__(self,name):
        return name in self.actions

    def constructAction(self,actionSetting):
        
        action = QAction(actionSetting.displayName,self.uimanager.mainwnd)
        if actionSetting.shortcut: 
            action.setShortcut(QKeySequence(actionSetting.shortcut))

        if actionSetting.module and actionSetting.funcName:
            module = __import__(actionSetting.module, fromlist=[actionSetting.funcName])
            funcobj = getattr(module, actionSetting.funcName)
            action.triggered.connect(lambda : funcobj(self.uimanager, action) )

        if actionSetting.toggleWidget:
            action.triggered.connect(lambda : self.uimanager.toggleWidget(actionSetting.toggleWidget))

        if actionSetting.showDialog:
            action.triggered.connect(lambda : self.uimanager.showDialog(actionSettings.showDialog))

        if actionSetting.showModal:
            action.triggered.connect(lambda : self.uimanager.showDialogModal(actionSetting.showModal))

        if actionSetting.checkable:
            action.setCheckable(True)


        return action




