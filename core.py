from bs4 import BeautifulSoup
from pyecore.resources.xmi import XMIResource
from pyecore.resources.json import JsonResource
from pyecore.resources import URI
from pyecore.ecore import EClass, EAttribute, EString, EObject, EReference, \
    EDataType, EEnum, EEnumLiteral, EPackage, EAnnotation, EBoolean, EInteger, EFloat
from pathlib import Path

XMIID = "xmi:id"
XMINAME = "name"
XMITYPE = "xmi:type"
PKGNAME = "ifc-ecore"
PKGPREFIX = "https://ifc-ecore.org/1.0"

class ElementPair(object):
    def __init__(self, id, source, target=None):
        self.id = id
        self.source = source
        self.target = target

class AddressableIndex(object):
    def __init__(self):
        self._ids = {}
    def getbyid(self, id):
        return self._ids.get(id, None)
    def addsource(self, id, el):
        self._ids[id] = ElementPair(id, el)
    def addtarget(self, id, el):
        self._ids[id].target = el
    def getsource(self, id):
        return self._ids[id].source
    def gettarget(self, id):
        return self._ids[id].target


### Predicates ###    

def isaddressable(el):
    return XMIID in el.attrs

def isnamed(el):
    return isaddressable(el) and (XMINAME in el.attrs)

def istyped(el):
    return XMITYPE in el.attrs

def iseclass(el):
    return isnamed(el) and el.attrs.get(XMITYPE) == "uml:Class" \
         and (not el.attrs.get("name").endswith("Enum")) \
             and el.attrs.get("name").startswith("Ifc") \
                 and not " " in el.attrs.get("name")

def iseattribute(el):
    return isnamed(el) and el.name == "ownedattribute" and el.attrs.get(XMITYPE) == "uml:Property"

def isereference(el):
    if not isnamed(el) or not el.attrs.get(XMITYPE) == "uml:Property": return False
    print(el.name)
    if el.name == "ownedend": return True 
    else: return False

def isedatatype(el):
    return isaddressable(el) and el.attrs.get(XMITYPE) == "uml:DataType"


def isepackage(el):
    return isaddressable(el) and el.attrs.get(XMITYPE) == "uml:Package"


def getxmidom(filepath):
    with open(filepath, "r") as f:
        return BeautifulSoup("".join(line.strip() for line in f.read().split("\n")), 'lxml')
        
           
   
def buildindex(dom):
    idx = AddressableIndex()
    for el in dom.find_all(isaddressable):
        idx.addsource(el.attrs[XMIID], el)
    return idx


def makepackage(dom, idx):
    pkg = EPackage(PKGNAME, nsURI=PKGPREFIX, nsPrefix=PKGNAME)
    for clstag in dom.find_all(iseclass):
        makeeclass(clstag, idx, pkg)
    return pkg


def makeeclass(clstag, idx, pkg):
    clsid = clstag.attrs[XMIID]

    cls = EClass(**makeclassproperties(clstag, idx, pkg))
    idx.addtarget(clsid, cls)
    pkg.eClassifiers.append(cls)

    for proptag in clstag.find_all(iseattribute):
        makeeattribute(proptag, idx, pkg, cls)

    return cls

def makeclassproperties(clstag, idx, pkg):
    props = {"name":clstag.attrs["name"], "superclass":None}
    # handle superclass lookup
    props["superclass"] = makegeneric(clstag, idx, pkg, None, "generalization", "general")
    return props

def makeeattribute(proptag, idx, pkg, cls):
    attr = EAttribute(**makeattributeproperties(proptag, idx, pkg, cls))
    idx.addtarget(proptag.attrs[XMIID], attr)
    cls.eStructuralFeatures.append(attr)
    return attr

def makeattributeproperties(proptag, idx, pkg, cls):
    props = {"name":None, "lower":0, "upper":1, "required":False, "eType":None, "ordered":True, "unique":True}

    lower = proptag.find("lowervalue")
    if lower:
        props["lower"] = int(lower.attrs["value"])

    upper = proptag.find("uppervalue")
    if upper:
        props["upper"] = upper.attrs["value"]
        props["upper"] = -1 if props["upper"] == "*" else int(props["upper"])

    props["eType"] = makeetype(proptag, idx, pkg, cls)
    props["name"] = proptag["name"]
    props["required"] = True if props["lower"] > 0 else False
    return props


def makeereference(proptag, idx, pkg, cls):
    attr = EReference(**makereferenceproperties(proptag, idx, pkg, cls))
    idx.addtarget(proptag.attrs[XMIID], attr)
    cls.eStructuralFeatures.append(attr)
    return attr

def makereferenceproperties(proptag, idx, pkg, cls):
    props = {"name":None, "eType":None, "containment":False,"eOpposite":None}
    props["eType"] = makegeneric(proptag, idx, pkg, cls, "type", "xmi:idref")
    props["name"] = proptag["name"]
    return props

def makeetype(proptag, idx, pkg, cls):
    proptype = proptag.find("type")
    if proptype:
        typeid = proptype.attrs["xmi:idref"]
        if not idx.gettarget(typeid):
            makeeclass(idx.getsource(typeid), idx, pkg) # process forward ref
            assert(idx.gettarget(typeid) != None)
        return idx.gettarget(typeid)
        
def makegeneric(proptag, idx, pkg, cls, tagname, attrname):
    proptype = proptag.find(tagname)
    if proptype:
        typeid = proptype.attrs[attrname]
        if not idx.gettarget(typeid):
            makeeclass(idx.getsource(typeid), idx, pkg) # process forward ref
            assert(idx.gettarget(typeid) != None)
        return idx.gettarget(typeid)

def save(pkg, targetfolder, name=PKGNAME):
    xmipath = str((targetfolder / (name +'.xmi')).resolve())
    jsonpath = str((targetfolder / (name +'.json')).resolve())
    xmi = XMIResource(URI(xmipath))
    json = JsonResource(URI(jsonpath))
    xmi.append(pkg)
    json.append(pkg)
    xmi.save()
    json.save()

     


if __name__ == "__main__":
    sourcepath = (Path(__file__).parent / 'models' / 'source' / 'uml.xml').resolve()
    targetfolder = (Path(__file__).parent / 'models' / 'targets')
    dom = getxmidom(sourcepath)
    idx = buildindex(dom)
    pkg = makepackage(dom, idx)
    save(pkg, targetfolder)





