import os

from PySide.QtCore import QObject

from PySide.QtGui import *
from PySide.QtCore import *

from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import BaseTextEdit

class PythonCodeEditor(BaseTextEdit):

    breakpointAdded = Signal(str, int)
    breakpointRemoved = Signal(str, int)

    def __init__(self,parent):
        super(PythonCodeEditor,self).__init__(parent)
        self.normalLineFormat = QTextBlockFormat()
        self.normalLineCharFormat = QTextCharFormat()
        self.currentLine=-1
        self.breakpointLines = set()
        self.codecName = ""
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

    def setBlockFormat(self,block,format = QTextBlockFormat(), charformat = QTextCharFormat() ):
        pos = block.position()
        cursor = self.textCursor()
        cursor.setPosition( pos, QTextCursor.MoveAnchor)
        cursor.movePosition( QTextCursor.EndOfBlock, QTextCursor.KeepAnchor )
        cursor.setBlockFormat(format)
        cursor.setCharFormat(charformat)

    def ensureLineVisible(self,lineno):
        block = self.document().findBlockByLineNumber(lineno-1)
        cursor = self.textCursor()
        cursor.setPosition( block.position(), QTextCursor.MoveAnchor)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def setCurrentLine(self,lineno):
        self.resetCurrentLine()
        block = self.document().findBlockByLineNumber(lineno-1)
        self.currentLine = lineno-1
        currentLineFormat = QTextBlockFormat()
        currentLineFormat.setBackground(QColor(self.currentLineBackground))
        currentLineCharFormat = QTextCharFormat()
        currentLineCharFormat.setForeground(QColor(self.currentLineColor))
        self.setBlockFormat( block, currentLineFormat, currentLineCharFormat )
        self.ensureLineVisible(lineno-1)

    def addBreakpointLine(self,lineno):

        lineno = lineno - 1

        self.breakpointLines.add(lineno)

        block = self.document().findBlockByLineNumber(lineno)

        if lineno != self.currentLine:
            bpLineFormat = QTextBlockFormat()
            bpLineFormat.setBackground(QColor(self.bpLineBackground))
            bpLineCharFormat = QTextCharFormat()
            bpLineCharFormat.setForeground(QColor(self.bpLineColor))
            self.setBlockFormat(block, bpLineFormat, bpLineCharFormat )

    def removeBreakpointLine(self,lineno):

        lineno = lineno - 1

        block = self.document().findBlockByLineNumber(lineno)

        if lineno != self.currentLine:
            self.setBlockFormat(block)

        self.breakpointLines.remove(lineno)

    def resetBreakpointLines(self):

        for line in self.breakpointLines:
            block = self.document().findBlockByLineNumber(line)
            self.setBlockFormat(block)
        self.breakpointLines.clear()

    def resetCurrentLine(self):
        if self.currentLine == -1:
            return

        block = self.document().findBlockByLineNumber(self.currentLine)

        if self.currentLine in self.breakpointLines:
            bpLineFormat = QTextBlockFormat()
            bpLineFormat.setBackground(QColor(self.bpLineBackground))
            bpLineCharFormat = QTextCharFormat()
            bpLineCharFormat.setForeground(QColor(self.bpLineColor))
            self.setBlockFormat(block, bpLineFormat, bpLineCharFormat )
        else:
            self.setBlockFormat( block)

        self.currentLine = -1


    def setErrorLine(self,lineno):
        pass

    def contextMenuEvent(self, event):

        def getSeFileEncoding(codecName):
            return lambda : self.setFileEncoding(codecName) 

        menu = self.createStandardContextMenu()
        encodingMenu = menu.addMenu("Encoding")

        codecNames = [codeName.data() for codeName in QTextCodec.availableCodecs()]
        codecNames.sort()

        for codecName in codecNames:
            name = codecName
            action = QAction(codecName, self)
            action.triggered.connect( getSeFileEncoding(codecName) )
            encodingMenu.addAction(action)

        textPosition = self.cursorForPosition(event.pos()).position()

        bpLineNo = reduce(lambda x,y: x +1 if y=="\n" else x, self.fileContent[:textPosition], 0)
        bpAction = QAction("Toggle breakpoint",self)
        bpAction.triggered.connect(lambda : self.setBreakpointOnLine(bpLineNo))
        menu.addAction(bpAction)

        menu.exec_(event.globalPos())

    def setFileEncoding(self,codecName):
        self.codecName = codecName
        self.loadFile(self.fileName)

    def setBreakpointOnLine(self,bpLineNo):
        if bpLineNo in self.breakpointLines:
            self.breakpointRemoved.emit(self.fileName, bpLineNo+1)
        else:
            self.breakpointAdded.emit(self.fileName, bpLineNo+1)

    def loadFile(self, fileName):

        self.fileName = fileName
        self.fileContent = ""

        no = 1
        with open(fileName) as f:
            for line in f:
                self.fileContent += "%-4d|  " % no + line
                no += 1
            #fileContent = reduce( lambda x,y: x + y, file)

        if self.codecName:
            codec = QTextCodec.codecForName(self.codecName)
        else:
            codec = QTextCodec.codecForLocale()

        self.fileContent = codec.toUnicode(self.fileContent)
        self.setPlainText(self.fileContent)

class SourceWidget( QDockWidget ):

    def __init__(self, uimanager, sourceFileName, *args):
        super(SourceWidget, self).__init__(*args)
        self.uimanager = uimanager
        self.mainWnd =uimanager.mainwnd
        self.sourceFileName = sourceFileName
        self.setWindowTitle(self.sourceFileName)
        self.sourceView = PythonCodeEditor(self)
        self.sourceView.breakpointAdded.connect(self.addBreakpoint)
        self.sourceView.breakpointRemoved.connect(self.removeBreakpoint)

        if self.sourceFileName:
            self.sourceView.loadFile(self.sourceFileName)
        self.setWidget( self.sourceView  )

    def setCurrentLine(self,lineno):
        self.sourceView.setCurrentLine(lineno)

    def onBreakpointLineAdded(self,lineno):
        self.sourceView.addBreakpointLine(lineno)

    def onBreakpointLineRemoved(self, lineno):
        self.sourceView.removeBreakpointLine(lineno)

    def addBreakpoint(self,filename,lineno):
        self.uimanager.debugClient.addBreakpoint(filename,lineno)

    def removeBreakpoint(self,filename,lineno):
        self.uimanager.debugClient.removeBreakpoint(filename,lineno)

    def resetCurrentLine(self):
        self.sourceView.resetCurrentLine()

    def setFileName(self,fileName):
        self.sourceFileName = fileName
        self.setWindowTitle(self.sourceFileName)

    def resetBreakpointLines(self):
        self.sourceView.resetBreakpointLines()

    def reload(self):
        self.sourceView.loadFile(self.sourceFileName)


class SourceManager(QObject):

    def __init__(self, widgetSettings, uimanager):
        QObject.__init__(self)
        self.uimanager = uimanager
        self.openSources = {}
        self.currentTragetSource = None
        self.currentPythonSource = None

        self.uimanager.targetStopped.connect(self.onTargetStopped)
        self.uimanager.targetRunning.connect(self.onTargetRunning)
        self.uimanager.targetDetached.connect(self.onTargetDetached)
        self.uimanager.targetThreadChanged.connect(self.onTargetDataChanged)
        self.uimanager.targetFrameChanged.connect(self.onTargetDataChanged)
        self.uimanager.targetBreakpointsChanged.connect(self.onTargetDataChanged)

        self.uimanager.pythonStopped.connect(self.onPythonStopped)
        self.uimanager.pythonRunning.connect(self.onPythonRunning)
        self.uimanager.pythonBreakpointAdded.connect(self.onPythonBreakpointAdded)
        self.uimanager.pythonBreakpointRemoved.connect(self.onPythonBreakpointRemoved)
        self.uimanager.pythonExit.connect(self.onPythonExit)
        self.uimanager.pythonStarted.connect(self.onPythonStarted)

        self.uimanager.showSourceRequired.connect(self.onSourceShow)

    def setVisible(self, vi):
        pass

    def onSourceShow(self, fileName):

        if fileName=="":
            return

        fileName = os.path.normcase(fileName)

        if fileName in self.openSources:
            source = self.openSources[fileName]
            source.reload()
            source.setVisible(True)
            source.raise_()
        else:
            source = SourceWidget(self.uimanager, fileName )
            self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea,source)
            source.setVisible(True)
            if len(self.openSources) > 0:
                self.uimanager.mainwnd.tabifyDockWidget( self.openSources.values()[0], source)
            self.openSources[fileName] = source

    @async
    def onTargetStopped(self):

        self.currentTragetSource = None

        fileName, line = yield ( self.uimanager.debugClient.callFunctionAsync( getSourceLine ) )
        if fileName == "":
            return

        try:

            if fileName in self.openSources:
                source = self.openSources[fileName]
            else:
                if os.path.exists(fileName):
                    source = SourceWidget(self.uimanager, fileName )
                    self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea,source)
                    if len(self.openSources) > 0:
                        self.uimanager.mainwnd.tabifyDockWidget(self.openSources.values()[0], source)
                    self.openSources[fileName] = source
                else:
                    shortName = os.path.split(fileName)[1]
                    for sourceName, widget in self.openSources.items():
                        if os.path.split(sourceName)[1] == shortName:
                            source = widget
                            break;
                    else:
                        return
        
            source.setVisible(True)
            source.raise_()
            source.setCurrentLine(line)

        except IOError:
            return

        self.currentTragetSource = source


    def onTargetDataChanged(self):
        self.onTargetStopped()

    def onTargetRunning(self):
        if self.currentTragetSource:
            self.currentTragetSource.resetCurrentLine()
            self.currentTragetSource = None

    def onTargetDetached(self):
        if self.currentTragetSource:
            self.currentTragetSource.resetCurrentLine()
            self.currentTragetSource = None


    @async
    def onPythonStopped(self):

        self.currentPythonSource = None

        fileName,line = yield( self.uimanager.debugClient.getPythonSourceLineAsync() )

        if fileName=="":
            return

        if fileName in self.openSources:
            source = self.openSources[fileName]

        else:
            try:
                source = SourceWidget(self.uimanager, fileName )
                self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea,source)
                if len(self.openSources) > 0:
                   self.uimanager.mainwnd.tabifyDockWidget(self.openSources.values()[0], source)
                self.openSources[fileName] = source
            except IOError:
                return

        source.setVisible(True)
        source.setCurrentLine(line)
        source.raise_()
        self.currentPythonSource = source


    def onPythonRunning(self):
        if self.currentPythonSource:
            self.currentPythonSource.resetCurrentLine()
            self.currentPythonSource = None

    def onPythonBreakpointAdded(self, filename, lineno):
        if filename in self.openSources:
            source = self.openSources[filename]
            source.onBreakpointLineAdded(lineno)

    def onPythonBreakpointRemoved(self, filename, lineno):
        if filename in self.openSources:
            source = self.openSources[filename]
            source.onBreakpointLineRemoved(lineno)

    def onPythonExit(self):
        for name, widget in self.openSources.items():
            widget.resetBreakpointLines()

    def onPythonStarted(self, fileName):

        if not fileName:
            return

        if fileName=="<string>":
            for fileName in self.openSources:
                source = self.openSources[fileName]
                source.reload()
                return

        if fileName in self.openSources:
            source = self.openSources[fileName]
            source.reload()
            source.setVisible(True)
        else:
            try:
                source = SourceWidget(self.uimanager, fileName )
                self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea,source)
                if len(self.openSources) > 0:
                   self.uimanager.mainwnd.tabifyDockWidget(self.openSources.values()[0], source)
                self.openSources[fileName] = source
            except IOError:
                return

        source.raise_()


def getSourceLine():
    import pykd
    try:
        ip = pykd.getFrame().ip
        fileName, fileLine, displacement = pykd.getSourceLine(ip)
        return (fileName, fileLine)
    except pykd.DbgException:
        return ("", 0)
