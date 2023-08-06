from PySide.QtGui import QFileDialog, QDialog, QWidget
from PySide.QtGui import QHBoxLayout, QVBoxLayout
from PySide.QtGui import QPushButton, QLineEdit, QDialogButtonBox, QTabWidget, QLabel
from PySide.QtCore import Qt

class OpenProcessDialog(QFileDialog):

    def __init__(self,settings,uimanager):
        super(OpenProcessDialog,self).__init__(uimanager.mainwnd)
        self.settings = settings
        self.uimanager = uimanager
        self.setNameFilter( "Executable (*.exe)" )

    def getProcessName(self):
        return self.getOpenFileName()[0]


class OpenDumpDialog(QFileDialog):

    def __init__(self,settings,uimanager):
        super(OpenDumpDialog,self).__init__(uimanager.mainwnd)
        self.settings = settings
        self.uimanager = uimanager

    def getFileName(self):
        return self.getOpenFileName()[0]


class OpenSourceDialog(QFileDialog):

    def __init__(self,settings,uimanager):
        super(OpenSourceDialog,self).__init__(uimanager.mainwnd)
        self.settings = settings
        self.uimanager = uimanager

    def getFileName(self):
        return self.getOpenFileName()[0]


class KernelDebuggingDialog(QDialog):

    class FirewireTab(QWidget):
        def __init__(self, parent=None):
            super(KernelDebuggingDialog.FirewireTab,self).__init__(parent)
            layout = QVBoxLayout()
            layout.addWidget( QLabel("Kernel debugging over a 1394 connection") )
            layout.addSpacing(10)
            layout.addWidget( QLabel("Channel") )
            self.channelEdit = QLineEdit("1")
            self.channelEdit.setMaximumWidth(60)
            self.channelEdit.textChanged.connect( lambda txt: self.parameterLabel.setText(self.getAttachString()) )
            layout.addWidget(self.channelEdit)
            layout.addSpacing(10)
            layout.addStretch()
            layout.addWidget(QLabel("Parameter:"))
            self.parameterLabel = QLabel(self.getAttachString())
            layout.addWidget(self.parameterLabel)
            self.setLayout(layout)

        def getAttachString(self):
            try:
                channel = int( self.channelEdit.text() )
                if channel in range(64):
                    return "1394:channel=%d" % channel
                else:
                    return "channel number must be in range (0-63)"
            except ValueError:
                return "channel number must be integer"

    class PipeTab(QWidget):
        def __init__(self, parent=None):
            super(KernelDebuggingDialog.PipeTab,self).__init__(parent)
            layout = QVBoxLayout()
            layout.addWidget( QLabel("Kernel debugging over named pipe") )
            layout.addSpacing(10)
            layout.addWidget( QLabel("Name:") )
            self.pipeName = QLineEdit("Com1")
            #self.pipeName.setMaximumWidth(120)
            self.pipeName.textChanged.connect( lambda txt: self.parameterLabel.setText(self.getAttachString()) )
            layout.addWidget(self.pipeName)
            layout.addSpacing(10)
            layout.addStretch()
            layout.addWidget(QLabel("Parameter:"))
            self.parameterLabel = QLabel(self.getAttachString())
            layout.addWidget(self.parameterLabel)
            self.setLayout(layout)

        def getAttachString(self):
            return r"com:pipe,resets=0,reconnect,port=\\.\pipe\%s" % self.pipeName.text()

    def  __init__(self, settings, uimanager):
        super(KernelDebuggingDialog,self).__init__(uimanager.mainwnd, Qt.WindowTitleHint)

        self.uimanager = uimanager

        layout1 = QVBoxLayout();

        self.parameterTab = QTabWidget()
        self.parameterTab.addTab( KernelDebuggingDialog.FirewireTab(), "1394")
        self.parameterTab.addTab( KernelDebuggingDialog.PipeTab(), "Pipe")

        layout1.addWidget(self.parameterTab)

        dialogBtn= QDialogButtonBox( QDialogButtonBox.Ok | QDialogButtonBox.Cancel )
        dialogBtn.accepted.connect(self.accept)
        dialogBtn.rejected.connect(self.reject)
        layout1.addWidget(dialogBtn)

        self.setLayout(layout1)
        self.accepted.connect(self.onAccepted)
        self.setWindowTitle("Attach to kernel")

    def onAccepted(self):
        commandLine = self.parameterTab.currentWidget().getAttachString()
        if commandLine:
            self.uimanager.debugClient.attachKernel(commandLine)



class FindDialog(QDialog):

    def __init__(self, settings, uimanager):
        super(FindDialog,self).__init__(uimanager.mainwnd, Qt.WindowTitleHint)
        self.uimanager = uimanager
        self.findEdit = QLineEdit()
        pushBtn = QPushButton("Find")
        pushBtn.clicked.connect(self.onFindBtn)
        layout =QHBoxLayout()
        layout.addWidget(pushBtn);
        layout.addWidget(self.findEdit);
        self.setLayout(layout)
        self.setTabOrder(self.findEdit, pushBtn)
        self.setWindowTitle("Find")
        self.fromStart = True

    def onFindBtn(self):
        if self.findEdit.text():
            self.uimanager.find(self.findEdit.text(), self.fromStart)
            self.fromStart = False


