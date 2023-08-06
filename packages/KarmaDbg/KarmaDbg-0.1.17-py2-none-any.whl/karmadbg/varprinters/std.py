from karmadbg.dbgcore.varprint import *
import pykd


@shortprinter(r"std::basic_string<char,std::char_traits<char>,std::allocator<char> >")
def stringShortPrinter(var):

    try:
        size = min(var._Mysize,100)
        if size <= 10:
            return "\"" + pykd.loadChars(var._Bx._Buf.getAddress(), size) + "\""
        else:
            return "\"" + pykd.loadChars(var._Bx._Ptr, size) + "\""
    except:
        return None


@shortprinter(r"std::basic_string<wchar_t,std::char_traits<wchar_t>,std::allocator<wchar_t> >")
def stringShortPrinter(var):

    try:
        size = min(var._Mysize,100)
        if size <= 10:
            return "\"" + pykd.loadWChars(var._Bx._Buf.getAddress(), size) + "\""
        else:
            return "\"" + pykd.loadWChars(var._Bx._Ptr, size) + "\""
    except:
        return None
