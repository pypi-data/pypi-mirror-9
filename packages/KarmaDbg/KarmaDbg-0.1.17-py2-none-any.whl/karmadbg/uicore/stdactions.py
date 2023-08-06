def onQuitAction(uimanager, action):
    uimanager.quit()

def onOpenProcessAction(uimanager, action):
    uimanager.openProcess()

def onOpenDumpAction(uimanager, action):
    uimanager.openDump()

def onGoAction(uimanager, action):
    uimanager.debugClient.go()

def onBreakAction(uimanager, action):
    uimanager.debugClient.breakin()

def onNextAction(uimanager, action):
    uimanager.debugClient.trace()

def onStepAction(uimanager, actionr):
    uimanager.debugClient.step()

def onStepOutAction(uimanager, action):
    uimanager.debugClient.stepout()

def onOpenAction(uimanager, action):
    uimanager.openSource()

def onStepSourceAction(uimanager, action):
    sourceMode = uimanager.debugClient.stepSourceMode
    uimanager.debugClient.stepSourceMode = not sourceMode
    action.setChecked(not sourceMode)

