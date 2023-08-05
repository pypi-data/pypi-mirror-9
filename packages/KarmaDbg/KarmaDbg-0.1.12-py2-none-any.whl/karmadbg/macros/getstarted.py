
import sys

step1 = '''
Hello!
It is a quick tour for karmadbg
The first thing you see is a python console
Try it:

>>>2+2
4

'''

step2 = '''
Karmadbg is based on the pykd and you can easily use it
with karmadbg.

>>>startProcess("notepad")
0
>>>go()
pykd.executionStatus.Break

Use F12 shortcut or the main menu to break a target execution
'''

step3 = '''
You can use any windbg expression:
>>>? 2+2
Evaluate expression: 4 = 00000000`00000004

Windbg metacommands ( except specific for the windbg command window as .cls):
>>>.echo 2+2
2+2

Windbg extension:
>>>!heap

To call windbg commands you can this trick (start command with ; ):
>>>;lm
start             end                 module name
00007ff6`17cc0000 00007ff6`17cfb000   notepad    (deferred)
00007ffc`29370000 00007ffc`293f2000   WINSPOOL   (deferred)
'''

def getstarted(*args):

    for step in [step1,step2,step3]:
        print step
    
        print "any key to proceed / Q to quit"
        if 'Q' == sys.stdin.readline():
            return

    print "It is all. Thank you for attention"
