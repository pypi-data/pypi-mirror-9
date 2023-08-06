from ZODB import FileStorage, DB
from ZEO.ClientStorage import ClientStorage
from Persistence import Persistent

import __main__
global dbroot
dbroot, objectsTypeMap=None, None

class CherryObject(Persistent): pass

class CherryObjectType:
    def __init__(self, objectType, fieldMap, tuneMap):
        self.objectType=objectType
        self.fieldMap=fieldMap
        self.tuneMap=tuneMap
    def newObject(self, **kw):
        obj=CherryObject()
        for key, value in kw.items():
            setattr(obj, key, value)
        self.saveObject(obj)
        return obj
    def getObjectById(self, id):
        return dbroot[self.objectType]['id'][int(id)]
    def getObjects(self, criteriaList=[]):
        if not dbroot.has_key(self.objectType): return []
        res=[]
        allObjects=dbroot[self.objectType]['id'].values()
        if not criteriaList: return allObjects
        for object in allObjects:
            for critName, critOp, critValue in criteriaList:
                if eval("object.%s %s critValue"%(critName, critOp, critValue)):
                    res.append(object)
        return res
    def getAllObjectsIdsAndLabels(self):
        res=[(0, "-- Please choose one --")]
        try: evalLabel=self.tuneMap["global"]["label"]
        except KeyError: evalLabel="object.name"
        for object in self.getObjects(): res.append((str(object.id), eval(evalLabel)))
        return res
    def printAllObjects(self):
        objectList=self.getObjects()
        for object in objectList:
             self.printObject(object)
    def printObject(self, object):
        print "************* %s object *********"%self.objectType
        print "id:",object.id
        for fieldName, fieldType in self.fieldMap.items():
            print fieldName+":",encodeValue(fieldType, getattr(object,fieldName))
        print

    def checkObject(self, object):
        pass # TBC

    def saveObject(self, object):
        print "Saving:", object
        # Put default values if some fields are missing
        object._p_changed=1
        for fieldName, fieldType in self.fieldMap.items():
            if not hasattr(object, fieldName): setattr(object, fieldName, decodeValue(fieldType, None))

        if hasattr(object,'id'):
            # It's an update
            #print "UPDATE"
            action="update"
            objectId=object.id
            previousObject=dbroot[self.objectType]['id'][objectId]
            self.removeObject(previousObject)
        else:
            # It's a new object
            # Set the object id
            if not dbroot.has_key(self.objectType):
                objectId=1
                dbroot[self.objectType]={}
                dbroot[self.objectType]['id']={}
            else:
                idList=dbroot[self.objectType]['id'].keys()
                if idList: objectId=max(idList)+1
                else: objectId=1
            object.id=objectId
        dbroot[self.objectType]['id'][objectId]=object

        # Add linkBack if any
        for fieldName, objectName, _fieldName, relation in self.getLinks():
            if relation.find("1to")==0:
                _object=getattr(object, fieldName)
                if _object!=None:
                    if relation.find("to1")==1:
                        setattr(_object, _fieldName, object)
                        _object._p_changed=1
                    elif relation.find("toN")==1:
                        getattr(_object, _fieldName).append(object)
                        _object._p_changed=1
            elif relation.find("Nto")==0:
                _objectList=getattr(object, fieldName)
                for _object in _objectList:
                    if _object!=None:
                        if relation.find("to1")==1:
                            setattr(_object, _fieldName, object)
                            _object._p_changed=1
                        elif relation.find("toN")==1:
                            getattr(_object, _fieldName).append(object)
                            _object._p_changed=1
            else: raise "ERROR"

        dummy=dbroot[self.objectType]
        dbroot[self.objectType]=dummy # Trick to force ZODB to resave that
        get_transaction().commit()

    # Delete an object
    def removeObject(self, object):
        # Remove old linkBack if any
        for fieldName, objectName, _fieldName, relation in self.getLinks():
            if relation.find("1to")==0:
                _object=getattr(object, fieldName)
                if _object!=None:
                    if relation.find("to1")==1 and object==getattr(_object, _fieldName)==object:
                        setattr(_object, _fieldName, None)
                        _object._p_changed=1
                    elif relation.find("toN")==1 and object in getattr(_object, _fieldName):
                        getattr(_object, _fieldName).remove(object)
                        _object._p_changed=1
            elif relation.find("Nto")==0:
                _objectList=getattr(object, fieldName)
                for _object in _objectList:
                    if _object!=None:
                        if relation.find("to1")==1 and object==getattr(_object, _fieldName)==object:
                            setattr(_object, _fieldName, None)
                            _object._p_changed=1
                        elif relation.find("toN")==1 and object in getattr(_object, _fieldName):
                            getattr(_object, _fieldName).remove(object)
                            _object._p_changed=1
            else: raise "ERROR"
        del dbroot[self.objectType]['id'][object.id]
        dummy=dbroot[self.objectType]
        dbroot[self.objectType]=dummy # Trick to force ZODB to resave that
        get_transaction().commit()

    def getLinks(self):
        res=[]
        for fieldName, fieldType in self.fieldMap.items():
            if fieldType.find('link to ')==0: relationLeft="1"
            elif fieldType.find('list of links to ')==0: relationLeft="N"
            else: continue
            if fieldType[-9:]==" linkBack": fieldType=fieldType[:-9]
            _objectName=fieldType.split()[-1].split('.')[0]
            _fieldName=fieldType.split('.')[-1]
            _fieldType=eval("%s.fieldMap"%_objectName)[_fieldName]
            if _fieldType.find('link to ')==0: relationRight="1"
            else: relationRight="N"
            res.append((fieldName, _objectName, _fieldName, relationLeft+"to"+relationRight))
        return res

def init(file, _objectsTypeMap, objectsTuneMap={}):
    global dbroot, objectsTypeMap
    #storage = FileStorage.FileStorage('Forum.fs')
    storage = ClientStorage(('localhost', 8090))
    db = DB(storage)
    conn = db.open()
    dbroot = conn.root()
    objectsTypeMap=_objectsTypeMap
    for objectType, fieldMap in objectsTypeMap.items():
        ot=objectType
        tuneMap=objectsTuneMap.get(objectType, {})
        cot=CherryObjectType(ot, fieldMap, tuneMap)
        setattr(__main__, ot, cot)
        globals()[ot]=cot

def initWeb(file, _objectsTypeMap, objectsTuneMap={}):
    init(file, _objectsTypeMap, objectsTuneMap)
    newMasksAndViews={'viewAllObjects':1, 'editObject':1, 'editObjectFormAction':1, 'addObject':1, 'deleteObject':1}
    for objectType, fieldMap in _objectsTypeMap.items():
        ot=objectType
        tuneMap=objectsTuneMap.get(objectType, {})
        cotw=__main__.CherryObjectTypeWeb(ot, fieldMap, tuneMap)
        setattr(__main__, ot, cotw)
        globals()[ot]=cotw

        __main__.maskAndViewMap[ot]=newMasksAndViews


# Convert a value to its "encoded" representation (for instance, a representation that can be used in a web form=
def encodeValue(fieldType, value):
    i=fieldType.find(" linkBack")
    if i!=-1: fieldType=fieldType[:i]
    if fieldType in ("string", "text", "float"):
        if not value: return ''
        return str(value)
    elif fieldType=="boolean":
        if not value: return "0"
        return "1"
    elif fieldType.find("link to ")==0:
        if not value: return "0"
        else: return str(value.id)
    elif fieldType.find("list of links to ")==0:
        if not value: return []
        objectName=fieldType.split()[-1].split('.')[0]
        if type(value)!=type([]): value=[value]
        res=[]
        for item in value: res.append(encodeValue("link to "+objectName, item))
        return res
    else: raise "ERROR: fieldType not implemented: %s"%fieldType

# Reverse function for encodeValue
def decodeValue(fieldType, value):
    i=fieldType.find(" linkBack")
    if i!=-1: fieldType=fieldType[:i]
    if fieldType in ("string", "text"):
        if not value: return ''
        return str(value)
    elif fieldType=="float":
        if not value: return 0
        return float(value)
    elif fieldType=="boolean":
        if not value: return 0
        return 1
    elif fieldType.find("link to ")==0:
        objectName=fieldType.split()[-1].split('.')[0]
        if not value or not int(value): return None
        return dbroot[objectName]['id'][int(value)]
    elif fieldType.find("list of links to ")==0:
        if not value: return []
        objectName=fieldType.split()[-1].split('.')[0]
        if type(value)!=type([]): value=[value]
        res=[]
        for item in value: res.append(decodeValue("link to "+objectName, item))
        return res
    else: raise "ERROR: fieldType not implemented: %s"%fieldType

def notEmpty(object, fieldName, tuneMap):
    if not getattr(object, fieldName): return "Missing"
    return ''

def sortOnAttribute(objectList, attribute, reverse=0):
    def s(i1, i2, attribute=attribute):
        if getattr(i1, attribute)>getattr(i2, attribute): return 1
        else: return -1
    objectList.sort(s)
    if reverse: objectList.reverse()

def removeFromUrl(url, paramName):
    i=url.find('&%s='%paramName)
    if i!=-1:
        j=url.find('&', i+1)
        if j==-1: return url[:i]                 # case "http://domain?....&a=b
        else: return url[:i]+url[j:]            # case "http://domain?...&a=b&...
    else:
        i=url.find('?%s='%paramName)
        if i!=-1:
            j=url.find('&', i)
            if j==-1: return url[:i]            # case "http://domain?a=b"
            else: return url[:i+1]+url[j+1:]    # case "http://domain?a=b&..."
    return url
        
def addToUrl(url, paramName, paramValue):
    url=removeFromUrl(url, paramName)
    if url.find('?')!=-1: c='&'
    else: c='?'
    return url+'%s%s=%s'%(c, paramName, paramValue)
