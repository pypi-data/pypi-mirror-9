import cgi

from PySide.QtGui import *
from PySide.QtCore import *

from karmadbg.uicore.async import async
from karmadbg.scripts.disasm import getDisasm
from karmadbg.scripts.breakpoint import getBreakpoints, setBreakpoint, removeBreakpoint
from karmadbg.uicore.basewidgets import NativeDataViewWidget


class QDisasmView (QTextEdit):

    SYMBOL_LINE = 0
    SOURCE_LINE = 1
    SOURCE_FILE = 2
    INSTRUCTION_LINE = 3
    DISASM_ERROR = 4

    htmlTemplate = \
    '''
        <!DOCTYPE html>
        <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <meta charset="utf-8" />
        <title></title>
        <style>
        %s
        </style>
        </head>
        <body>
        %s
        </body>
        </html>
    '''

    def __init__(self, uimanager, parent = None):
        super(QDisasmView, self).__init__(parent)
        self.uimanager = uimanager
        self.disasmCache = []
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.showSymbols = False
        self.showSourceLines = False
        self.showBreakpoints = False
        self.updateMutex = QMutex()
        self.backwardDisasm = True

    def getVisibleLineCount(self):
        cursor = self.textCursor()
        fontMetric = QFontMetrics( cursor.charFormat().font()) 
        lineHeight = fontMetric.height()
        return self.height() / lineHeight

    @async
    def viewUpdate(self):

        if not self.isEnabled():
            return

        if not self.updateMutex.tryLock():
            return

        self.breakpointLines = yield (self.uimanager.debugClient.callFunctionAsync(getBreakpoints) )

        lineCount = self.getVisibleLineCount()

        while not self.inCache(self.disasmIp, lineCount, self.delta - (lineCount/2) ):

            disasmCount = lineCount if lineCount > 20 else 20
            if len(self.offsetCache) == 0 or self.delta == 0:
                startDisasm = self.disasmIp
                disasmLines = yield ( self.uimanager.debugClient.callFunctionAsync(getDisasm, 2*disasmCount + 10 , -disasmCount - 10, startDisasm ) )
                disasmLines = disasmLines[10:]
            elif self.delta < 0:
                if self.backwardDisasm:
                    startDisasm = self.offsetCache[0][0] if len(self.offsetCache) else self.disasmIp
                    disasmLines = yield ( self.uimanager.debugClient.callFunctionAsync(getDisasm, disasmCount + 10, -disasmCount - 10, startDisasm ) )
                    disasmLines = disasmLines[10:]
                else:
                    disasmLines = []
            else:
                startDisasm = self.offsetCache[-1][0] if len(self.offsetCache) else self.disasmIp
                disasmLines = yield ( self.uimanager.debugClient.callFunctionAsync(getDisasm, disasmCount, 1, startDisasm ) )

            if len(disasmLines) == 0:
                self.backwardDisasm = False
                self.disasmLines = self.getFromCache( self.offsetCache[0][0], lineCount-1, 0 )
                self.disasmLines.insert(0, (0, self.DISASM_ERROR, None))
                self.textUpdate()
                deltaOffset = self.disasmLines[len(self.disasmLines)/2][0]
                deltaIndex = self.offsetCache.index( (deltaOffset, self.INSTRUCTION_LINE,) ) 
                startIndex = self.offsetCache.index( (self.disasmIp, self.INSTRUCTION_LINE,) ) 
                self.delta = deltaIndex - startIndex
                self.updateMutex.unlock()
                return
            else:
                self.updateCache(disasmLines)

        self.disasmLines = self.getFromCache( self.disasmIp, lineCount, self.delta - (lineCount/2) )
        self.textUpdate()

        self.updateMutex.unlock()


    @async
    def dataUpdate(self,expression):

        self.delta = 0
        self.offsetCache = []
        self.disasmCache = {}
        self.disasmIp = 0
        self.currentIp = 0
        self.backwardDisasm = True

        if expression:
            self.disasmIp = yield(self.uimanager.debugClient.getExpressionAsync(expression) )
            if not self.disasmIp:
                self.clearView()
                return
        else:
            frame = yield( self.uimanager.debugClient.getCurrentFrameAsync() )
            self.currentIp = frame[0]
            self.disasmIp = self.currentIp

        self.viewUpdate()

    def textUpdate(self):

        bodyText = ""
        for lineOffset, lineType, lineData in self.disasmLines:
            if lineType == self.SYMBOL_LINE:
                bodyText += self.highLightSymbol(lineOffset, lineData)
            elif lineType == self.SOURCE_FILE:
                bodyText += self.highLightFile(lineOffset, lineData)
            elif lineType == self.INSTRUCTION_LINE:
                bodyText += self.highLightAsm(lineOffset, lineData)
            elif lineType == self.DISASM_ERROR:
                bodyText += self.highlightError(lineOffset, "can not disasm" )

        htmlText = self.htmlTemplate % ( self.uimanager.docCss, bodyText)
        self.setHtml(htmlText)

    def highLightSymbol(self, symbolOffset, symbolStr):
        str = "<pre><div class=\"symbol\">%s</div></pre>" % cgi.escape(symbolStr)
        return str

    def highLightFile(self, symbolOffset, fileData):
        str = "<pre><div class=\"sourcefile\">%s</div></pre>" % cgi.escape( "%s Line: %d" % fileData )
        return str

    def highLightAsm(self, asmOffset, asmStr):
        if asmOffset == self.currentIp:
            str = "<pre><div class=\"current\">%s</div></pre>" % cgi.escape(asmStr)
        elif self.showBreakpoints and asmOffset in self.breakpointLines:
            str = "<pre><div class=\"breakpoint\">%s</div></pre>" % cgi.escape(asmStr)
        else:
            str = "<pre>%s</pre>" % asmStr
        return str

    def highlightError(self, errorOffset, errorStr):
        str = "<pre><div class=\"error\">%s</div></pre>" % cgi.escape(errorStr)
        return str

    def updateCache(self, disasmLines):

        for offset, instruction, symbol, fileName, lineNo in disasmLines:

            if self.showSymbols and symbol and (offset, self.SYMBOL_LINE) not in self.offsetCache:
                 self.offsetCache.insert(0, (offset, self.SYMBOL_LINE))

            if self.showSourceLines and fileName and (offset, self.SOURCE_FILE) not in self.offsetCache:
                 self.offsetCache.insert(0, (offset, self.SOURCE_FILE))

            if (offset, self.INSTRUCTION_LINE) not in self.offsetCache:
                self.offsetCache.insert(0, (offset, self.INSTRUCTION_LINE))

            self.disasmCache[offset] = ( instruction, symbol, fileName, lineNo)

        self.offsetCache.sort()


    def getFromCache(self, offset, lineCount, delta):

        index = self.offsetCache.index( (offset, self.INSTRUCTION_LINE,) ) + delta

        lst = []
        for i in xrange(index, index+lineCount):
            offset, lineType = self.offsetCache[i]
            if lineType == self.SYMBOL_LINE:
                instruction, symbol, fileName, lineNo = self.disasmCache[offset] 
                lst.append( (offset, lineType, symbol,) )
            elif lineType == self.SOURCE_FILE:
                instruction, symbol, fileName, lineNo = self.disasmCache[offset] 
                lst.append( (offset, lineType, (fileName,lineNo),) )
            elif lineType ==  self.INSTRUCTION_LINE:
                instruction, symbol, fileName, lineNo = self.disasmCache[offset] 
                lst.append( (offset, lineType, instruction,) )

        return lst

    def inCache(self, offset, lineCount, delta):

        if (offset, self.INSTRUCTION_LINE) not in self.offsetCache:
            return False

        index = self.offsetCache.index( (offset, self.INSTRUCTION_LINE,) )
        if index + delta < 0 or index + delta >= len(self.offsetCache):
            return False

        index = index + delta

        if index + lineCount > len(self.offsetCache):
            return False

        return True

    def clearView(self):
        self.setPlainText("")

    def resizeEvent (self, resizeEvent):
        super(QDisasmView, self).resizeEvent(resizeEvent)
        self.viewUpdate()

    def wheelEvent( self, wheelEvent ):
        numSteps = wheelEvent.delta() / 50
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
        offset, lineType, lineData= self.disasmLines[lineNo]
        if lineType == self.INSTRUCTION_LINE:
            bpAction = QAction("Toggle breakpoint",self)
            bpAction.triggered.connect(lambda : self.toggleBreakpointOnOffset(offset))
            menu.addAction(bpAction)
        elif lineType == self.SOURCE_FILE:
            sourceAction = QAction("Open source",self)
            sourceAction.triggered.connect(lambda : self.uimanager.showSourceRequired.emit(lineData[0]))
            menu.addAction(sourceAction)

        menu.exec_(event.globalPos())

    def toggleBreakpointOnOffset(self, offset):
        if offset in self.breakpointLines:
            self.uimanager.debugClient.callFunction(removeBreakpoint, offset)
        else:
            self.uimanager.debugClient.callFunction(setBreakpoint, offset)

    def setShowSymbols(self,checked):
        self.showSymbols = checked
        self.offsetCache = []
        self.disasmCache = {}
        self.viewUpdate()

    def setShowSourceLine(self,checked):
        self.showSourceLines = checked
        self.offsetCache = []
        self.disasmCache = {}
        self.viewUpdate()

    def setShowBreakpoint(self,checked):
        self.showBreakpoints = checked
        self.viewUpdate()

class DisasmWidget(NativeDataViewWidget):
    def __init__(self, widgetSettings, uimanager):
        super(DisasmWidget, self).__init__(uimanager)
        self.uimanager = uimanager
        self.disasmView = QDisasmView(uimanager, parent = self)
        self.setWindowTitle("Disassmbler")
        self.disasmView.setReadOnly(True)
        self.disasmView.showSymbols = True
        self.disasmView.showSourceLines = False
        self.disasmView.showBreakpoints = True

        self.exprEdit = QLineEdit()
        self.exprEdit.returnPressed.connect(self.dataUpdate)

        self.settingBox = QMenuBar()
        self.settingMenu= QMenu("Settings")
        symbolAction = QAction("Show symbols",self)
        symbolAction.setCheckable(True)
        symbolAction.setChecked(self.disasmView.showSymbols)
        symbolAction.toggled.connect(self.disasmView.setShowSymbols)
        self.settingMenu.addAction(symbolAction)

        sourceAction = QAction("Show source lines",self)
        sourceAction.setCheckable(True)
        sourceAction.setChecked(self.disasmView.showSourceLines)
        sourceAction.toggled.connect(self.disasmView.setShowSourceLine)
        self.settingMenu.addAction(sourceAction)

        bpAction = QAction("Show breakpoints",self)
        bpAction.setCheckable(True)
        bpAction.setChecked(self.disasmView.showBreakpoints)
        bpAction.toggled.connect(self.disasmView.setShowBreakpoint)
        self.settingMenu.addAction(bpAction)

        self.settingBox.addMenu(self.settingMenu)
        self.settingBox.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.exprEdit)
        hlayout.addWidget(self.settingBox)

        vlayout = QVBoxLayout()
        vlayout.addLayout(hlayout)
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

    def onBreakpointChanged(self):
        self.disasmView.viewUpdate()
