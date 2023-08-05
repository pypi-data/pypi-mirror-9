
import sys
import os
import traceback
import inspect

def showsyntaxerror(exc_info):
    list=[]
    try:
        type, value, tb = exc_info
        list = traceback.format_exception_only(type, value)
    finally:
        pass

    return "".join(list)

def showexception(exc_info):
    list=[]
    try:
        type, value, tb = exc_info
        list = traceback.format_exception_only(type, value)
    finally:
        pass

    return "".join(list)


def showtraceback(exc_info, hideStack=1):
    list=[]

    try:
        type, value, tb = exc_info
        tblist = traceback.extract_tb(tb)
        del tblist[:hideStack]
        list = traceback.format_list(tblist)
        if list:
            list.insert(0, "Traceback (most recent call last):\n")
        list[len(list):] = traceback.format_exception_only(type, value)
    finally:
        tblist = tb = None
    return "".join(list)

def firstChanceExc(exc_info):
    list = []
    try:
        type, value, tb = exc_info
        tblist = traceback.extract_tb(tb)
        return len(tblist) == 1
    except:
        pass
    return False


def isstandard_exception(exc_info):
    type, value, tb = exc_info
    return os.path.normcase(os.path.join( os.path.dirname(sys.executable), "lib" ) ) == os.path.normcase( os.path.split(tb.tb_frame.f_code.co_filename)[0] )

def pyGetSourceLine(exc_info):
    type, value, tb = exc_info
    return (tb.tb_frame.f_code.co_filename, (tb.tb_frame.f_lineno))

