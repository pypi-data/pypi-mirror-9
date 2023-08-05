from PySide.QtGui import *
from PySide.QtCore import *
from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import NativeDataViewWidget


#class LocalVarsWidget(NativeDataViewWidget):

#    def __init__(self, widgetSettings, uimanager):
#        super(LocalVarsWidget, self).__init__(uimanager)
#        self.uimanager = uimanager

#        self.treeViewModel = QStandardItemModel(0,4)
#        for section, title in { 0 : "Name", 1 : "Value", 2 : "Type", 3 : "Location"}.items():
#            self.treeViewModel.setHorizontalHeaderItem( section, QStandardItem(title) )

#        self.treeView = QTreeView()
#        self.treeView.setModel(self.treeViewModel)

#        self.setWidget(self.treeView)
#        self.setWindowTitle(widgetSettings.title)
#        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

#    def dataUnavailable(self):
#        self.treeViewModel.setRowCount(0)

#    @async
#    def dataUpdate(self):
#        self.treeViewModel.setRowCount(0)
#        vars = yield( self.uimanager.callFunction(getLocals) )

#        for var in vars:
#            self.treeViewModel.appendRow( [ QStandardItem(i) for i in var ] )

class LocalVarsWidget(NativeDataViewWidget):

    def __init__(self, widgetSettings, uimanager):
        super(LocalVarsWidget, self).__init__(uimanager)
        self.uimanager = uimanager

        self.textView = QPlainTextEdit(parent=self)
        self.textView.setReadOnly(True)
        self.textView.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.setWidget(self.textView)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUnavailable(self):
        self.textView.setPlainText("")

    @async
    def dataUpdate(self):
        vars = yield( self.uimanager.debugClient.callFunctionAsync(getLocals ) )
        t = ""
        for var in vars:
            t += "%-20s%s\n" % var
        self.textView.setPlainText(t)

def getLocals():
    import pykd
    try:
        locals = pykd.getFrame().getLocals()
        return [ ( name, str(value) ) for name, value in locals ]
    except pykd.DbgException:
        return []