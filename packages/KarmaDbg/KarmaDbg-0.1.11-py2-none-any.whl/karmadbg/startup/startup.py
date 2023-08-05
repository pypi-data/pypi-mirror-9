import os
import pykd 

from karmadbg.dbgcore.settings import DbgSettings

def startup():

    homedir = os.path.join( os.path.expanduser("~"), ".karmadbg")
    settingsFile = os.path.join( homedir, "default.xml" )
    dbgSettings = DbgSettings()
    dbgSettings.loadSettings(settingsFile)

    if hasattr(dbgSettings, "dbgEngExtensions") and len(dbgSettings.dbgEngExtensions) > 0:
        print ""
        print "loading DbgEng extensions:"
        for ext in dbgSettings.dbgEngExtensions:
            if ext.startup:
                cmdStr = ".load %s" % ext.path
                print cmdStr
                pykd.dbgCommand(cmdStr)
        print ""
