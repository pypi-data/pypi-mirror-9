from PySide.QtGui import *
from PySide.QtCore import *
from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import NativeDataViewWidget


class MemoryDmpWidget(NativeDataViewWidget):

    def __init__(self, widgetSettings, uimanager):
        super(MemoryDmpWidget,self).__init__(uimanager)
        self.uimanager = uimanager

        frame = QFrame(parent=self)

        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        self.exprEdit = QLineEdit()
        self.exprEdit.returnPressed.connect(self.dataUpdate)
        hlayout.addWidget(self.exprEdit)
        self.combo = QComboBox()
        self.combo.addItem("Byte")
        self.combo.addItem("Byte Signed")
        self.combo.addItem("Byte Hex")
        self.combo.addItem("Byte Char")
        self.combo.currentIndexChanged.connect(lambda x : self.dataUpdate())
        hlayout.addWidget(self.combo)
        hlayout.setSpacing(4)
        hlayout.setContentsMargins(0,0,0,0)
        vlayout.addLayout(hlayout)
        self.hexTextEdit = QPlainTextEdit()
        self.hexTextEdit.setReadOnly(True)
        #self.hexTextEdit.setStyleSheet("border: 0px;")
        vlayout.addWidget(self.hexTextEdit)
        vlayout.setSpacing(4)
        vlayout.setContentsMargins(4,4,4,4)
        frame.setLayout(vlayout)
        
        self.setWindowTitle("Memory")
        self.setWidget(frame)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUnavailable(self):
        self.hexTextEdit.setPlainText("")

    @async
    def dataUpdate(self):
        memdmp = []
        expr = self.exprEdit.text()
        if expr:
            if self.combo.currentIndex() == 0:
                memdmp = yield( self.uimanager.debugClient.callFunctionAsync(getBytes, expr, 0x1000) )
                if memdmp:
                    text = reduce(lambda x, y: x + "%d " % y, memdmp, "")
                    self.hexTextEdit.setPlainText(text)
            if self.combo.currentIndex() == 1:
                memdmp = yield( self.uimanager.debugClient.callFunctionAsync(getSignBytes, expr, 0x1000) )
                if memdmp:
                    text = reduce(lambda x, y: x + "%d " % y, memdmp, "")
                    self.hexTextEdit.setPlainText(text)
            if self.combo.currentIndex() == 2:
                memdmp = yield( self.uimanager.debugClient.callFunctionAsync(getBytes, expr, 0x1000) )
                if memdmp:
                    text = reduce(lambda x, y: x + "%02X " % y, memdmp, "")
                    self.hexTextEdit.setPlainText(text)
            if self.combo.currentIndex() == 3:
                memdmp = yield( self.uimanager.debugClient.callFunctionAsync(getChars, expr, 0x1000) )
                if memdmp:
                    text = reduce(lambda x, y: x + "%s " % ( "?" if ord(y) < 32 else y ), memdmp, "")
                    self.hexTextEdit.setPlainText(text)

        if memdmp == []:
            self.hexTextEdit.setPlainText("")
        if memdmp == None:
            self.hexTextEdit.setPlainText("Unavailable memory")

def getBytes(expr,length):

    import pykd

    try:
        exprVal = pykd.expr(expr)
    except pykd.DbgException:
        return None

    try:
        return pykd.loadBytes(pykd.addr64(exprVal),length)
    except pykd.MemoryException:
        return None

def getSignBytes(expr,length):

    import pykd

    try:
        exprVal = pykd.expr(expr)
    except pykd.DbgException:
        return None

    try:
        return pykd.loadSignBytes(pykd.addr64(exprVal),length)
    except pykd.MemoryException:
        return None

def getChars(expr,length):
    import pykd

    try:
        exprVal = pykd.expr(expr)
    except pykd.DbgException:
        return None

    try:
        return pykd.loadChars(pykd.addr64(exprVal),length)
    except pykd.MemoryException:
        return None


