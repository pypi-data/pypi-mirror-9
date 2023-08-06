import xml.etree.ElementTree as xmltree

class DbgSettings(object):

    def __init__(self):
        self.rootxml = None

    def loadSettings(self, fileName, policy='default'):

        { 
            'default' : self.loadDefaultSettings,
            'overwrite' : self.loadOverwriteSettings,
        }.get(policy, self.loadDefaultSettings)(fileName)


    def loadDefaultSettings(self, fileName):
        try:
            self.rootxml = xmltree.parse(fileName).getroot()
        except IOError:
           self.rootxml = xmltree.fromstring('<Settings></Settings>')


    def loadOverwriteSettings(self, fileName):
        try:
            rootxml = xmltree.parse(fileName).getroot()
        except IOError:
            rootxml = xmltree.fromstring('<Settings></Settings>')

        if self.rootxml is None:
            self.rootxml = rootxml
            return
        self.rootxml = mergeXml(self.rootxml, rootxml)

    @property
    def mainWindow(self):
        xmlelem=self.rootxml.find("./MainWindow")
        return DbgMainWindowSettings(xmlelem)

    @property
    def dbgEngExtensions(self):
        xmlelem=self.rootxml.find("./DbgEngExtensions")
        return [ DbgEngExtensionSetting(ext) for ext in xmlelem.findall("./Extension") ]

    @property
    def widgets(self):
        xmlelem=self.rootxml.find("./Widgets")
        return [ WidgetSettings(widget) for widget in xmlelem.findall("./Widget") ]

    @property
    def actions(self):
        xmlelem=self.rootxml.find("./Actions")
        return [ ActionSettings(action) for action in xmlelem.findall("./Action") ]

    @property
    def dialogs(self):
        xmlelem=self.rootxml.find("./Dialogs")
        return [ DialogSettings(action) for action in xmlelem.findall("./Dialog") ]

    @property
    def style(self):
        return DbgStyleSettings(self.rootxml.find("./Style"))

    @property
    def doccss(self):
        return DbgStyleSettings(self.rootxml.find("./DocCss"))

    @property
    def textCodec(self):
        xmlelem = self.rootxml.find("./TextCodec")
        return DbgTextCodecSettings(xmlelem) if xmlelem != None else None

    @property
    def mainMenu(self):
        return MainMenuSettings(self.rootxml.find("./MainMenu"))
    

class DbgMainWindowSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def width(self):
        return getIntAttribute( self.xmlelem, "width", 800 )

    @property
    def height(self):
        return getIntAttribute( self.xmlelem , "height", 600 )

    @property
    def title(self):
        return getStrAttribute( self.xmlelem , "title", "Window Title" )


class MainMenuSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def className(self):
        return getStrAttribute(self.xmlelem, "className")

    @property
    def menuItems(self):
        return [ MenuItemSettings(item) for item in self.xmlelem.findall("./MenuItem") ]


class MenuItemSettings(object):

    def __init__(self,xmlelem):
        self.xmlelem=xmlelem

    @property
    def name(self):
        return getStrAttribute( self.xmlelem , "name")

    @property
    def actionName(self):
        return getStrAttribute( self.xmlelem , "actionName")

    @property
    def displayName(self):
        return getStrAttribute( self.xmlelem , "displayName")
        
    @property
    def separator(self):
        return getBoolAttribute(self.xmlelem, "separator")

    @property
    def toggleWidget(self):
        return getStrAttribute(self.xmlelem, "toggleWidget")

    @property
    def menuItems(self):
        return [ MenuItemSettings(item) for item in self.xmlelem.findall("./MenuItem") ]

class DbgStyleSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def fileName(self):
        return getStrAttribute(self.xmlelem, "fileName") if self.xmlelem != None else ""

    @property
    def text(self):
        return getStrAttribute(self.xmlelem, "text") if self.xmlelem != None else ""

class DbgTextCodecSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name") if self.xmlelem != None else ""

    

class DbgEngExtensionSetting(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name", self.path )

    @property
    def path(self):
        return getStrAttribute(self.xmlelem, "path")

    @property
    def startup(self):
        return getBoolAttribute(self.xmlelem, "startup")


class WidgetSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name")

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def className(self):
        return getStrAttribute(self.xmlelem, "className")

    @property
    def behaviour(self):
        return getStrAttribute(self.xmlelem, "behaviour")

    @property
    def visible(self):
        return getBoolAttribute(self.xmlelem, "visible")

    @property
    def title(self):
        return getStrAttribute(self.xmlelem, "title")

class DialogSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name")

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def className(self):
        return getStrAttribute(self.xmlelem, "className")


class ActionSettings(object):
    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
        return getStrAttribute(self.xmlelem, "name")

    @property
    def displayName(self):
        return getStrAttribute(self.xmlelem, "displayName", self.name )

    @property
    def shortcut(self):
        return getStrAttribute(self.xmlelem, "shortcut")

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def funcName(self):
        return getStrAttribute(self.xmlelem, "funcName")

    @property
    def toggleWidget(self):
        return getStrAttribute(self.xmlelem, "toggleWidget")

    @property
    def showDialog(self):
        return getStrAttribute(self.xmlelem, "showDialog")

    @property
    def showModal(self):
        return getStrAttribute(self.xmlelem, "showModal")

    @property
    def checkable(self):
        return getBoolAttribute(self.xmlelem, "checkable")

def getIntAttribute(xmlelem,name,default=0):
    try:
        val = xmlelem.get( name, default )
        return int(val)
    except ValueError:
        pass

    try:
        return int(val,16)
    except ValueError:
        pass

    return default

def getStrAttribute(xmlelem,name,default=""):
    return str( xmlelem.get( name, default ) )

def getBoolAttribute(xmlelem, name, default=False):
    val=xmlelem.get(name)
    if val==None:
        return default
    return val.lower()=="true"


def mergeXml( xmlnode_dest, xmlnode_src):

    for node_src in xmlnode_src:
        for node_dest in xmlnode_dest:
            if node_src.tag == node_dest.tag:
                if len(node_dest)>0 and len(node_src)>0:
                    mergeXml(node_dest, node_src)
                    break
                elif node_dest.attrib==node_src.attrib:
                    break
        else:
            xmlnode_dest.append(node_src)

    return xmlnode_dest

