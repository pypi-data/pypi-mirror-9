from PySide.QtGui import *
from PySide.QtCore import *
from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import NativeDataViewWidget, AutoQMutex
from karmadbg.dbgcore.varprint import *

class VarItem(QStandardItem):

    def __init__(self, uimanager, varName, varType, varLocation):
        super(VarItem,self).__init__(varName)
        self.uimanager = uimanager
        self.name = varName
        self.type = varType
        self.location = varLocation


class LocalVarsWidget(NativeDataViewWidget):

    def __init__(self, widgetSettings, uimanager):
        super(LocalVarsWidget, self).__init__(uimanager)
        self.uimanager = uimanager

        self.treeModel = QStandardItemModel(0,4)
        self.buildHeader()

        self.treeView = QTreeView()
        self.treeView.setModel(self.treeModel)

        self.treeView.expanded.connect(self.onExpandItem)

        self.setWidget(self.treeView)
        self.setWindowTitle(widgetSettings.title)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)
        self.updateMutex = QMutex()

    def dataUnavailable(self):
        self.treeModel.clear()
        self.buildHeader()

    def buildHeader(self):
        for section, title in { 0 : "Name", 1 : "Value", 2 : "Type", 3 : "Location"}.items():
            self.treeModel.setHorizontalHeaderItem( section, QStandardItem(title) )

    @async
    def dataUpdate(self):

        if not self.updateMutex.tryLock():
            return

        with AutoQMutex(self.updateMutex) as mutexGuard:

            self.treeModel.clear()
            self.buildHeader()

            vars = yield( self.uimanager.debugClient.callFunctionAsync(getLocals ) )
            for varName, varValue, varType, varLocation in vars:
                rootItem = VarItem(self.uimanager, varName,varType,varLocation)
                row = [ rootItem, QStandardItem(varValue), QStandardItem(varType), QStandardItem(hex(varLocation)) ]
                fields = yield( self.uimanager.debugClient.callFunctionAsync(getFields, rootItem.type, rootItem.location ) )
                for fieldName, fieldValue, fieldType, fieldLocation in fields:
                    fieldItem = VarItem(self.uimanager, fieldName, fieldType, fieldLocation)
                    fieldRow = [ fieldItem, QStandardItem(fieldValue), QStandardItem(fieldType), QStandardItem(hex(fieldLocation)) ]
                    rootItem.appendRow(fieldRow)
                self.treeModel.appendRow(row)

            self.treeView.resizeColumnToContents(0)
        
    @async
    def onExpandItem(self, modelIndex):
        item = self.treeModel.itemFromIndex(modelIndex)
        for r in range(item.rowCount()):
            childItem = item.child(r)
            if not childItem.hasChildren():
                fields = yield( self.uimanager.debugClient.callFunctionAsync(getFields, childItem.type, childItem.location ) )
                for fieldName, fieldValue, fieldType, fieldLocation in fields:
                    fieldItem = VarItem(self.uimanager, fieldName, fieldType, fieldLocation)
                    row = [ fieldItem, QStandardItem(fieldValue), QStandardItem(fieldType), QStandardItem(hex(fieldLocation)) ]
                    childItem.appendRow(row)


class WatchWidget(NativeDataViewWidget):
    def __init__(self, widgetSettings, uimanager):
        super(WatchWidget, self).__init__(uimanager)
        self.uimanager = uimanager

        self.treeModel = QStandardItemModel(0,4)
        self.buildHeader()

        self.treeModel.itemChanged.connect(self.onItemChanged)

        self.treeView = QTreeView()
        self.treeView.setModel(self.treeModel)
        self.treeView.expanded.connect(self.onExpandItem)

        self.emptyItem = QStandardItem("")
        self.treeModel.appendRow(self.emptyItem)

        self.setWidget(self.treeView)
        self.setWindowTitle(widgetSettings.title)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)
        self.updateMutex = QMutex()
        
    def onItemChanged(self,item):
        if item is self.emptyItem:
            self.emptyItem = QStandardItem("")
            self.treeModel.appendRow(self.emptyItem)
            self.dataUpdate()
        elif item.column() == 0 and item.text() == "":
            self.treeModel.removeRow(item.row())

    def dataUnavailable(self):
        pass

    def buildHeader(self):
        for section, title in { 0 : "Name", 1 : "Value", 2 : "Type", 3 : "Location"}.items():
            self.treeModel.setHorizontalHeaderItem( section, QStandardItem(title) )

    @async
    def dataUpdate(self):

        if not self.updateMutex.tryLock():
            return

        with AutoQMutex(self.updateMutex) as mutexGuard:

            for r in range(self.treeModel.rowCount() - 1):
                varName = self.treeModel.item(r).text() 
                varName, varValue, varType, varLocation = yield( self.uimanager.debugClient.callFunctionAsync(getTypedVar, varName ) )
                rootItem = VarItem(self.uimanager, varName, varType, varLocation)
                self.treeModel.setItem( r, 0, rootItem)
                self.treeModel.setItem( r, 1, QStandardItem(varValue) )
                self.treeModel.setItem( r, 2, QStandardItem(varType) )
                self.treeModel.setItem( r, 3, QStandardItem(hex(varLocation)) )

                fields = yield( self.uimanager.debugClient.callFunctionAsync(getFields, rootItem.type, rootItem.location ) )
                for fieldName, fieldValue, fieldType, fieldLocation in fields:
                    fieldItem = VarItem(self.uimanager, fieldName, fieldType, fieldLocation)
                    row = [ fieldItem, QStandardItem(fieldValue), QStandardItem(fieldType), QStandardItem(hex(fieldLocation)) ]
                    rootItem.appendRow(row)

            self.treeView.resizeColumnToContents(0) 

    @async
    def onExpandItem(self, modelIndex):

        item = self.treeModel.itemFromIndex(modelIndex)
        for r in range(item.rowCount()):
            childItem = item.child(r)
            if not childItem.hasChildren():
                fields = yield( self.uimanager.debugClient.callFunctionAsync(getFields, childItem.type, childItem.location ) )
                for fieldName, fieldValue, fieldType, fieldLocation in fields:
                    fieldItem = VarItem(self.uimanager, fieldName, fieldType, fieldLocation)
                    row = [ fieldItem, QStandardItem(fieldValue), QStandardItem(fieldType), QStandardItem(hex(fieldLocation)) ]
                    childItem.appendRow(row)
    

    