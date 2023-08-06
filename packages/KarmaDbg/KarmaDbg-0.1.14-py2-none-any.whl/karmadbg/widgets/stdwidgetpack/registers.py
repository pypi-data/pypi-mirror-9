
from PySide.QtGui import *
from PySide.QtCore import *
from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import NativeDataViewWidget

class QRegistersView(QPlainTextEdit):

    def __init__(self, uimanager, parent = None):
        super(QRegistersView, self).__init__(parent)
        self.uimanager = uimanager
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

    @async
    def updateView(self):
        regs = yield ( self.uimanager.debugClient.getRegistersAsync() )
        regstxt = ""
        for regName, regValue in regs:
            regstxt += "%s: %d (%x)\n" % (regName, regValue, regValue)
        self.setPlainText(regstxt)

    def clear(self):
        self.setPlainText("")


class RegistersWidget(NativeDataViewWidget):

    def __init__(self, widgetSettings, uimanager):
        super(RegistersWidget, self).__init__(uimanager)
        self.uimanager = uimanager
        self.registerView = QRegistersView(uimanager, parent = self)
        self.setWindowTitle("Registers")
        self.setWidget(self.registerView )
        self.registerView.setReadOnly(True)
        self.registerView.setDisabled(True)

        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUpdate(self):
        self.registerView.updateView()

    def dataUnavailable(self):
        self.registerView.clear()
