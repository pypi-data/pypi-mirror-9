from PySide.QtGui import QDockWidget, QVBoxLayout, QLineEdit, QPlainTextEdit, QFrame
from PySide.QtCore import Qt

from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import NativeDataViewWidget

class PythonEvalWidget(NativeDataViewWidget):
    
    def __init__(self,widgetSettings, uimanager):

        super(PythonEvalWidget,self).__init__(uimanager)

        self.uimanager = uimanager

        vlayout = QVBoxLayout()

        self.evalEdit = QLineEdit()
        self.evalEdit.returnPressed.connect(self.onReturnPressed)
        vlayout.addWidget(self.evalEdit)

        self.evalResult = QPlainTextEdit()
        self.evalResult.setReadOnly(True)
        vlayout.addWidget(self.evalResult)
  
        vlayout.setSpacing(4)
        vlayout.setContentsMargins(4,4,4,4)

        self.frame = QFrame()
        self.frame.setLayout(vlayout)

        self.setWidget(self.frame)

        self.setWindowTitle("Eval expression")
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def onReturnPressed(self):
        self.dataUpdate()

    def dataUnavailable(self):
        self.evalResult.setPlainText("")

    @async
    def dataUpdate(self):
        expr = self.evalEdit.text()
        if expr:
            res = yield( self.uimanager.debugClient.pythonEvalAsync(expr) )
            self.evalResult.setPlainText(res)
        else:
            self.evalResult.setPlainText("")


