from PySide.QtGui import *
from PySide.QtCore import *

from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import BaseTextEdit
from karmadbg.scripts.disasm import getDisasm
from karmadbg.scripts.breakpoint import getBreakpoints, setBreakpoint, removeBreakpoint
from karmadbg.uicore.basewidgets import NativeDataViewWidget

class QDisasmView (BaseTextEdit):

    def __init__(self, uimanager, parent = None):
        super(QDisasmView, self).__init__(parent)
        self.uimanager = uimanager
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)


    def getVisibleLineCount(self):
        cursor = self.textCursor()
        fontMetric = QFontMetrics( cursor.charFormat().font()) 
        lineHeight = fontMetric.height()
        return self.height() / lineHeight

    @async
    def dataUpdate(self, expression):

        self.delta = 0

        if expression:
            self.currentIp = yield(self.uimanager.debugClient.getExpressionAsync(expression) )
            if not self.currentIp:
                self.clearView()
                return
        else:
            frame = yield( self.uimanager.debugClient.getCurrentFrameAsync() )
            self.currentIp = frame[0]

        lineCount = self.getVisibleLineCount()

        firstLineRelPos = -(lineCount/2)

        self.disasmLines = yield ( self.uimanager.debugClient.callFunctionAsync(getDisasm, lineCount, firstLineRelPos,  self.currentIp ) )

        if len(self.disasmLines) == 0:
            self.clearView()
            return

        self.breakpointLines = yield (self.uimanager.debugClient.callFunctionAsync(getBreakpoints) )

        text = "\n".join((value[1] for value in self.disasmLines))

        self.setPlainText(text)

        self.highlightText()
        
    @async
    def viewUpdate(self):

        if not self.isEnabled():
            return

        lineCount = self.getVisibleLineCount()

        firstLineRelPos = -(lineCount/2) - self.delta

        self.disasmLines = yield ( self.uimanager.debugClient.callFunctionAsync(getDisasm, lineCount, firstLineRelPos, self.currentIp ) )

        if len(self.disasmLines) == 0:
            self.clearView()
            return

        text = "\n".join((value[1] for value in self.disasmLines))

        self.setPlainText(text)

        self.highlightText()


    def clearView(self):

        self.setPlainText("")

        
    def highlightText(self):

        for i in xrange(len(self.disasmLines)):
            offset, _ = self.disasmLines[i]
            if offset == self.currentIp:
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.Start)
                cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor, i)
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

                blockFormat = QTextBlockFormat()
                blockFormat.setBackground(QColor(self.currentLineBackground))
                cursor.setBlockFormat(blockFormat)
            
                charFormat = QTextCharFormat()
                charFormat.setForeground(QColor(self.currentLineColor))
                cursor.setCharFormat(charFormat)

            if offset in self.breakpointLines:
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.Start)
                cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor, i)
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

                blockFormat = QTextBlockFormat()
                blockFormat.setBackground(QColor(self.bpLineBackground))
                cursor.setBlockFormat(blockFormat)
            
                charFormat = QTextCharFormat()
                charFormat.setForeground(QColor(self.bpLineColor))
                cursor.setCharFormat(charFormat)


    def resizeEvent (self, resizeEvent):
        super(QDisasmView, self).resizeEvent(resizeEvent)
        self.viewUpdate()

    def wheelEvent( self, wheelEvent ):
        numDegrees = wheelEvent.delta() / 8
        numSteps = numDegrees / 20
        self.delta += numSteps
        self.viewUpdate()

    def keyPressEvent(self,event):

        lineCount = self.getVisibleLineCount()

        if event.key() == Qt.Key_Up:
            self.delta -= 1
            self.viewUpdate()
            return

        if event.key() == Qt.Key_Down:
            self.delta += 1
            self.viewUpdate()
            return

        if event.key() == Qt.Key_PageUp:
            self.delta -= lineCount
            self.viewUpdate()
            return

        if event.key() == Qt.Key_PageDown:
            self.delta += lineCount
            self.viewUpdate()
            return

        super(QDisasmView, self).keyPressEvent(event)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        textPosition = self.cursorForPosition(event.pos()).position()
        lineNo = reduce(lambda x,y: x +1 if y=="\n" else x, self.toPlainText()[:textPosition], 0)
        offset = self.disasmLines[lineNo][0]
        bpAction = QAction("Toggle breakpoint",self)
        bpAction.triggered.connect(lambda : self.toggleBreakpointOnOffset(offset))
        menu.addAction(bpAction)

        menu.exec_(event.globalPos())

    def toggleBreakpointOnOffset(self, offset):
        if offset in self.breakpointLines:
            self.uimanager.debugClient.callFunction(removeBreakpoint, offset)
        else:
            self.uimanager.debugClient.callFunction(setBreakpoint, offset)


class DisasmWidget(NativeDataViewWidget):
    def __init__(self, widgetSettings, uimanager):
        super(DisasmWidget, self).__init__(uimanager)
        self.uimanager = uimanager
        self.disasmView = QDisasmView(uimanager, parent = self)
        self.setWindowTitle("Disassmbler")
        self.disasmView.setReadOnly(True)

        self.exprEdit = (QLineEdit())
        self.exprEdit.returnPressed.connect(self.dataUpdate)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.exprEdit )
        vlayout.addWidget(self.disasmView)
        vlayout.setSpacing(4)
        vlayout.setContentsMargins(4,4,4,4)

        frame = QFrame()
        frame.setLayout(vlayout)

        self.setWidget(frame)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUnavailable(self):
        self.disasmView.clearView()

    def dataUpdate(self):
        self.disasmView.dataUpdate(expression = self.exprEdit.text() )


