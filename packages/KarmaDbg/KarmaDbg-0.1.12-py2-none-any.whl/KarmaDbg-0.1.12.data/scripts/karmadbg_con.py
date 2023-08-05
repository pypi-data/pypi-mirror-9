import sys
import os
import time

from threading import Thread

from karmadbg.dbgcore.settings import DbgSettings
from karmadbg.dbgcore.dbgengine import DbgEngine, ConsoleDebugClient, LocalDebugServer


def dbgLoop(dbgEngine):

    import karmadbg
    print "KarmaDbg console client. Version %s" % karmadbg.__version__ 

    dbgControl = dbgEngine.getServer().getServerControl()
    dbgControl.startup()

    while True:

        inputStr = raw_input(">>>")
        
        while True:

            result = dbgControl.debugCommand( inputStr )

            if result.IsNeedMoreData:
                s = raw_input("...")
                inputStr += '\n' + s
                continue

            if result.IsQuit:
                print "stop debugger"
                dbgEngine.stop()
                return

            break

def main():

    import karmadbg
    dirname = os.path.dirname(karmadbg.__file__)
    defaultSettingFile = os.path.join( dirname, "settings", "default.xml" )
    homedir = os.path.join( os.path.expanduser("~"), ".karmadbg")
    userSettingsFile = os.path.join( homedir, "default.xml" )

    dbgSettings = DbgSettings()
    dbgSettings.loadSettings(defaultSettingFile)
    dbgSettings.loadSettings(userSettingsFile, policy='overwrite')

    dbgClient = ConsoleDebugClient()
    dbgServer = LocalDebugServer()

    dbgEngine = DbgEngine( dbgClient, dbgServer, dbgSettings )

    dbgEngine.start();

    thread = Thread(target=dbgLoop, args=(dbgEngine,) )
    thread.start()

    while True:
        try:
            thread.join(1000000)
            break
        except KeyboardInterrupt:
            dbgEngine.getServer().getServerInterrupt().breakin()

    thread.join()


if __name__ == "__main__":
    main()

