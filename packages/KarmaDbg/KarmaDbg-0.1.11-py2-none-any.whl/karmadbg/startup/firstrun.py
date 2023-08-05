
import os
import shutil
from karmadbg.macros.license import license as read_license
from karmadbg.macros.getstarted import getstarted as get_started
from karmadbg.macros.config import config

def firstrun():
    pass
    #config(["clear"])



#firstrun()



#def firstrun():

#    if os.path.exists( getHomeDir() ):
#        return
   
#    print ""
#    print "Hello"
#    print "This is the first KarmaDbg run."
#    print "Press \"S\" to make settings"
#    print "Press \"D\" to create deafult settings"
 
#    res = raw_input("S/D>")

#    if res == 'S':
#        manual_setup()
#    else:
#        default_setup()

#def manual_setup():
#    try:
#        default_setup()
#        print "Setup successfully completed"
#    except:
#        print "Failed to complete setup. Clear all"
#        config("clear")

#    print "Do you like to read license? \"Y/N\""

#    res = raw_input("Y/N>")
#    if res == 'Y':
#        print read_license()

#    print "Do you like to get a quick tour for karmadbg? \"Y/N\""

#    res = raw_input("Y/N>")
#    if res == 'Y':
#        print get_started()

#def default_setup():
#    os.mkdir(getHomeDir())
#    shutil.copy( os.path.join(getSourceDir(), "default.xml"), os.path.join(getHomeDir(), "default.xml") )

#def getHomeDir():
#    homedir = os.path.expanduser("~")
#    return os.path.join(homedir, ".karmadbg") 

#def getSourceDir():
#    import karmadbg
#    return os.path.join( os.path.dirname(karmadbg.__file__), "settings")



