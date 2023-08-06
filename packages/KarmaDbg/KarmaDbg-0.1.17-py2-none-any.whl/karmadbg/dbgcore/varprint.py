import pykd
import re
import pkgutil


def getLocals():
    try:
        locals = pykd.getFrame().getParams() + pykd.getFrame().getLocals()
        return [ (name, getShortPrinter(value), value.type().name(), value.getAddress()) for name, value in locals ]

    except pykd.DbgException:
        return []

def getTypedVar(varName):
    try:
        var = pykd.typedVar(varName)
        return (varName, getShortPrinter(var), var.type().name(), var.getAddress(),)
    except pykd.DbgException:
        return (varName, "unavailable", "unknown", 0)


def getFields(typeName, offset):

    try:

        var = pykd.typedVar(typeName, offset)

        #find registred multiline printer

        if var.type().isUserDefined():
           return  structFieldPrinter(var)

        if var.type().isArray():
            return arrayElementPrinter(var)

        return defaultMultilinePrinter(var)

    except pykd.DbgException:

        return []


def getShortPrinter(var):

    for shortPrinter in shortPrinterList:

        if re.match( shortPrinter[0], var.type().name() ):
            retVal = shortPrinter[1](var)
            if retVal != None:
                return retVal
        
    if var.type().isBase():
        return baseVarPrinter(var)

    if var.type().isPointer():
        return pointerVarPrinter(var)

    return defaultShortPrinter(var)


def defaultShortPrinter(var):
    return ""

def baseVarPrinter(var):
    try:
        if var.isInteger():
            return str(long(var))
        else:
            return str(float(var))
    except pykd.MemoryException:
        return "access violation"

def pointerVarPrinter(var):
    if pykd.isValid(var):
        return hex(var)
    else:
        return "invalid memory (0x%x)" % var

def defaultMultilinePrinter(var):
    return []

def structFieldPrinter(var):
    return [ (fieldName, getShortPrinter(fieldValue), fieldValue.type().name(), fieldValue.getAddress(),)  for fieldName, fieldOffset, fieldValue in var.fields() ]

def arrayElementPrinter(var):
    lst = []
    for i in xrange(min(20,len(var))):
        val = var[i]
        lst.append( ( "[%d]" % (i), getShortPrinter(val), val.type().name(), val.getAddress(), ) )
    return lst

shortPrinterList = []

def shortprinter(*typeNames):
    
    def decorator(fn):

        for typeName in typeNames:
            shortPrinterList.append( (typeName,fn,) )

        def wrapper(var):

            return fn(var)

        return wrapper

    return decorator

def registerShortPrinters():
    
    import karmadbg.varprinters

    for loader, module_name, ispkg in pkgutil.iter_modules( karmadbg.varprinters.__path__):
        if not ispkg:
            loader.find_module(module_name).load_module(module_name)
 
registerShortPrinters()





















