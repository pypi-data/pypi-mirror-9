
from PySide.QtCore import Qt
from PySide.QtGui import QStandardItemModel, QStandardItem, QTreeView

from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import PythonDataViewWidget

class PythonLocalsWidget(PythonDataViewWidget):

    def __init__(self, widgetSettings, uimanager): 
        super(PythonLocalsWidget,self).__init__(uimanager)

        self.uimanager = uimanager

        self.treeModel = QStandardItemModel(0,2)

        self.treeView = QTreeView()
        self.treeView.setModel(self.treeModel)
        self.treeView.expanded.connect(self.onExpandItem)
        self.buildHeader()

        self.setWidget(self.treeView)

        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUnavailable(self):
        self.treeModel.clear()

    @async
    def dataUpdate(self):
        self.treeModel.clear()
        self.buildHeader()
        localvars= yield( self.uimanager.debugClient.getPythonLocalsAsync( () ) )
        for name, value in localvars:
            row = [ QStandardItem(name), QStandardItem(self.valueToStr(value)) ]
            subitems = yield( self.uimanager.debugClient.getPythonLocalsAsync( (name,) ))
            for name, value in subitems:
                row[0].appendRow( [ QStandardItem(name), QStandardItem(self.valueToStr(value)) ] )
            self.treeModel.appendRow(row)
        self.treeView.setModel(self.treeModel)
        self.resizeColumns()
     
    def buildHeader(self):
        for section, title in { 0 : "Name", 1 : "Value"}.items():
             self.treeModel.setHorizontalHeaderItem(section, QStandardItem(title))

    def resizeColumns(self):
        self.treeView.resizeColumnToContents(0)      
        self.treeView.setColumnWidth( 0, self.treeView.columnWidth(0) + 20 )

    @async
    def onExpandItem(self, modelIndex):
        item = self.treeModel.itemFromIndex(modelIndex)
        names = [ item.text() ]
        parent = item.parent()
        while parent:
            names.insert(0, parent.text())
            parent = parent.parent()
        for r in range(item.rowCount()):
            childItem = item.child(r)
            if childItem.hasChildren():
                continue
            subitems = yield( self.uimanager.debugClient.getPythonLocalsAsync( names + [childItem.text()] ))
            for name, value in subitems:
                childItem.appendRow( [ QStandardItem(name), QStandardItem(self.valueToStr(value)) ] )
        self.resizeColumns()

    def valueToStr(self, value):
        s =  str(value)
        s = s.replace("\n", "\\n")
        s = s.replace("\r", "\\r")
        s = s.replace("\t", "\\t")
        return s
 