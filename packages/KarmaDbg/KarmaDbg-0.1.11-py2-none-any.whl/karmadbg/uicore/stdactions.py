def onQuitAction(uimanager):
    uimanager.quit()

def onOpenProcessAction(uimanager):
    uimanager.openProcess()

def onOpenDumpAction(uimanager):
    uimanager.openDump()

def onGoAction(uimanager):
    uimanager.debugClient.go()

def onBreakAction(uimanager):
    uimanager.debugClient.breakin()

def onNextAction(uimanager):
    uimanager.debugClient.trace()

def onStepAction(uimanager):
    uimanager.debugClient.step()

def onOpenAction(uimanager):
    uimanager.openSource()
