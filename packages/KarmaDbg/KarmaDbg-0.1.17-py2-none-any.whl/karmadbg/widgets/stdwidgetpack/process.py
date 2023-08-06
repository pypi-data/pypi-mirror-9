
from PySide.QtGui import QTreeView, QStandardItemModel, QStandardItem
from PySide.QtCore import Qt

from karmadbg.uicore.basewidgets import NativeDataViewWidget
from karmadbg.uicore.async import async

from karmadbg.scripts.proclist import getProcessThreadList, setCurrentThread


class BreakpointItem(QStandardItem):

    def __init__(self, bpOffset):
        super(BreakpointItem, self).__init__("%x" % bpOffset)
        self.bpOffset = bpOffset

class BreakpointRootItem(QStandardItem):
    def __init__(self, pid):
        super(BreakpointRootItem,self).__init__("Breakpoints: 0")
        self.pid = pid
        self.setEditable(False)

    def update(self, bpList):
        self.setRowCount(0)
        for bp in bpList:
            bpItem = BreakpointItem(bp)
            self.appendRow(bpItem)

        self.setText("Breakpoints: %d" % len(bpList))
        self.sortChildren(0)

class ThreadItem(QStandardItem):
    def __init__(self, pid, tid):
        super(ThreadItem,self).__init__("Id: %x" % tid)
        self.pid = pid
        self.tid = tid
        self.setEditable(False) 
        self.setSelectable(False)

    def update(self, isCurrent):
        font = self.font()
        font.setBold(isCurrent)
        self.setFont(font)

class ThreadRootItem(QStandardItem):
    def __init__(self, pid):
        super(ThreadRootItem,self).__init__("Threads: 0")
        self.pid = pid
        self.setEditable(False)

    def update(self, threadlst, currentThread):

        #delete stopped threads
        row = 0
        while row < self.rowCount():
            threadItem = self.child(row)
            for tid in threadlst:
                if tid == threadItem.tid:
                    row += 1
                    continue
            else:
                self.removeRow(row)

        #added new threads
        for tid, in threadlst:

            row = 0
            while row < self.rowCount():
                threadItem = self.child(row)
                if threadItem.tid == tid:
                    break
                row += 1
            else:
                threadItem = ThreadItem(self.pid, tid)
                self.appendRow(threadItem)

            threadItem.update(currentThread == tid)

        self.setText("Threads: %d" % len(threadlst))
        self.sortChildren(0)


class ProcessItem(QStandardItem):
    def __init__(self, pid, exe):
        super(ProcessItem,self).__init__("Pid: %x (%s)" % (pid, exe) )
        self.pid = pid
        self.exe = exe
        self.setEditable(False)
        self.processNameItem = QStandardItem( "Name: %s" % exe )
        self.processNameItem.setEditable(False)
        self.appendRow(self.processNameItem)
        self.threadsItem = ThreadRootItem(pid)
        self.appendRow(self.threadsItem)
        self.breakpointsItem = BreakpointRootItem(pid)
        self.appendRow(self.breakpointsItem)

    def updateThreads(self, threadlst, currentThread):
        self.threadsItem.update(threadlst, currentThread)

    def updateBreakpoints(self, breakpointLst):
        self.breakpointsItem.update(breakpointLst)

class ProcessExplorerWidget(NativeDataViewWidget):

    def __init__(self, widgetSettings, uimanager):
        super(ProcessExplorerWidget,self).__init__(uimanager)
        self.uimanager = uimanager

        self.treeView = QTreeView()
        self.treeView.setHeaderHidden(True)

        self.treeModel = QStandardItemModel(0,1)

        self.treeView.setSelectionMode(QTreeView.NoSelection)
        self.treeView.setAllColumnsShowFocus(False)
        self.treeView.doubleClicked.connect(self.onItemDblClick)

        self.setWidget(self.treeView)

        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUnavailable(self):
        self.treeModel.clear()

       
    @async
    def dataUpdate(self):
        processesSnapshot = yield(self.uimanager.debugClient.callFunctionAsync(getProcessThreadList) )

        for processInfo in processesSnapshot.processList:

            row = 0
            while row < self.treeModel.rowCount():
                processItem = self.treeModel.item(row)
                if processItem.pid == processInfo.pid:
                    break
                row += 1
            else:
                processItem = ProcessItem(processInfo.pid, processInfo.exeName)
                self.treeModel.appendRow(processItem)

            processItem.updateThreads(processInfo.threadList, processesSnapshot.currentThreadID if processesSnapshot.currentProcessID == processInfo.pid else None )
            processItem.updateBreakpoints(processInfo.breakpointList)

        self.treeView.setModel(self.treeModel)

    def onItemDblClick(self, modelIndex):
        item = self.treeModel.itemFromIndex(modelIndex)
        if type(item) is ThreadItem:
            self.uimanager.debugClient.callFunction(setCurrentThread, item.pid, item.tid)


