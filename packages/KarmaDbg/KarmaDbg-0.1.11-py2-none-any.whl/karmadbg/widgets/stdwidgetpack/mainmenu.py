
from PySide.QtCore import QObject
from PySide.QtGui import QMenu
from PySide.QtGui import QAction

class MainMenuManager(QObject):
    
    def __init__(self, mainMenuSettings, uimanager):
        QObject.__init__(self)
        self.menuBar = uimanager.mainwnd.menuBar()
        self.uimanager = uimanager

        for menuSettings in mainMenuSettings.menuItems:
            self.addMenuGroup(self.menuBar,menuSettings)

    def addMenuGroup(self, parent, menuSettings):
        menu = QMenu(menuSettings.displayName)
        parent.addMenu(menu)
        for menuItem in menuSettings.menuItems:
            if menuItem.separator:
                menu.addSeparator()
            elif len(menuItem.menuItems) > 0:
                self.addMenuGroup(menu, menuItem)
            elif menuItem.toggleWidget:
                widget = self.uimanager.getWidget(menuItem.toggleWidget)
                menu.addAction(widget.toggleViewAction())
            else:
                menu.addAction( self.uimanager.actions[menuItem.actionName] )


