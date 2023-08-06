use HttpAuthenticate, Tools

CherryClass CherryObjectsWeb(HttpAuthenticate) abstract:
mask:
    def index(self):
        <py-exec="request.sessionMap['index']=self.getPath()">
        <py-for="objectType in CherryObjects.objectsTypeMap.keys()">
            <b><py-eval="objectType"></b>:
            <a py-attr="'%s/viewAllObjects'%objectType" href="">View/Update</a>&nbsp;&nbsp;
            <a py-attr="'%s/addObject'%objectType" href="">Add</a><br>
        </py-for>
view:
    def action(self, objectType, action, **kw):
        ot=globals()[objectType]
        return getattr(ot, action)(**kw)
function:
    def getPasswordListForLogin(self, login):
        return 1

CherryClass CherryObjectTypeWeb(CherryObjects.CherryObjectType,HttpAuthenticate) abstract:
mask:
    def viewObjectList(self, objectList, mask=None):
        <py-exec="if not mask: mask=self.defaultListMask">
        <py-for="object in objectList">
            <py-eval="apply(mask, (object, _index, _end))">
        </py-for>

    def defaultListMask(self, object, index, end):
        <py-if="index==0">
            <table border=1><tr>
            <th>id</th>
            <py-for="fieldName, fieldType in self.fieldMap.items()">
                <th py-eval="fieldName"></th>
            </py-for>
            <th>Edit</th>
            <th>Delete</th>
            </tr>
        </py-if>
        <tr>
        <td py-eval="object.id"></td>
        <py-for="fieldName, fieldType in self.fieldMap.items()">
            <py-exec="print 'getattr(%s, %s)'%(object,fieldName), ':', getattr(object, fieldName)">
            <td py-eval="self.displayValue(fieldType, getattr(object,fieldName))"></td>
        </py-for>
        <td><a py-attr="'editObject?objectId=%s'%object.id" href="">Edit</td>
        <td><a py-attr="'deleteObject?objectId=%s'%object.id" href="">Delete</td>
        </tr>
        <py-if="index==end">
            </table>
        </py-if>

    def editObjectForm(self, _object, hasError, okUrl, errorUrl, formTuneMap={}):
        <py-code="
            if not hasError:
                request.sessionMap['formTuneMap']=formTuneMap
                self.setTuneMapItem(formTuneMap, "global", "hasError", 0)
                self.setTuneMapItem(formTuneMap, "global", "okUrl", okUrl)
                self.setTuneMapItem(formTuneMap, "global", "errorUrl", errorUrl)
                object=_object
            else:
                formTuneMap=request.sessionMap['formTuneMap']
                object=formTuneMap['global']['object']
        ">
        <form method="post" name="cherryForm" py-attr="request.base+'/'+self.objectType+'/editObjectFormAction'" action="">
        <py-if="hasattr(object, 'id')">
            <input type=hidden name=id py-attr="object.id" value="">
        </py-if>
        <py-eval="self.renderFields(object, formTuneMap)">
        </form>

view:
    def editObjectFormAction(self, **kw):
        object=CherryObjects.CherryObject()
        formTuneMap=request.sessionMap['formTuneMap']
        globalError, hasError=0,0
        for fieldName, fieldType in self.fieldMap.items():
            fieldValue=kw.get(fieldName, None)
            fieldValue=CherryObjects.decodeValue(fieldType, fieldValue)
            setattr(object, fieldName, fieldValue)
        if kw.has_key('id'): object.id=int(kw['id'])
        validateFuncList=self.getTuneMapItem(formTuneMap, "global", "validate")
        if validateFuncList:
            if type(validateFuncList)!=type([]): validateFuncList=[validateFuncList]
            for validateFunc in validateFuncList:
                globalError=validateFunc(object)
                if globalError: hasError=1
        for fieldName in self.fieldMap.keys():
            fieldValue=kw.get(fieldName, None)
            # check field
            validateFuncList=self.getTuneMapItem(formTuneMap, fieldName, "validate")
            error=""
            if validateFuncList:
                if type(validateFuncList)!=type([]): validateFuncList=[validateFuncList]
                for validateFunc in validateFuncList:
                    error=validateFunc(*(object, fieldName, formTuneMap))
            self.setTuneMapItem(formTuneMap, fieldName, "error", error)
            if error: hasError=1
        self.setTuneMapItem(formTuneMap, "global", "error", globalError)
        self.setTuneMapItem(formTuneMap, "global", "hasError", hasError)
        self.setTuneMapItem(formTuneMap, "global", "object", object)
        if hasError: url=CherryObjects.addToUrl(formTuneMap['global']['errorUrl'], 'hasError', '1')
        else:
            print "self:", self, self == message
            self.saveObject(object)
            url=formTuneMap['global']['okUrl']
        response.headerMap['status']=302
        response.headerMap['location']=url
        return ""

    def viewAllObjects(self):
        objectList=self.getObjects()
        return self.viewObjectList(objectList)

    def editObject(self, objectId=0, hasError=0):
        res=""
        if not hasError:
            object=self.getObjectById(objectId)
        else:
            error=self.getTuneMapItem(request.sessionMap['formTuneMap'], "global", "error")
            res="<font color=red><b>Please correct the errors</b></font><br><br>"
            if error: res+="<font color=red>%s</font><br><br>"%error
            object=None
        return res+self.editObjectForm(object, hasError, request.sessionMap['index'], 'editObject')

    def addObject(self, hasError=0):
        res=""
        if not hasError:
            object=CherryObjects.CherryObject()
        else:
            error=self.getTuneMapItem(request.sessionMap['formTuneMap'], "global", "error")
            res="<font color=red><b>Please correct the errors</b></font><br><br>"
            if error: res+="<font color=red>%s</font><br><br>"%error
            object=None
        return res+self.editObjectForm(object, hasError, request.sessionMap['index'], 'addObject')

    def deleteObject(self, objectId):
        object=self.getObjectById(objectId)
        self.removeObject(object)
        response.headerMap['status']=302
        response.headerMap['location']=request.sessionMap['index']
        return ""

function:
    def getPasswordListForLogin(self, login):
        return 1
    def setTuneMapItem(self, tuneMap, fieldName, propertyName, propertyValue):
        if not tuneMap.has_key(fieldName): tuneMap[fieldName]={}
        tuneMap[fieldName][propertyName]=propertyValue
    def getTuneMapItem(self, tuneMap, fieldName, propertyName, default=None):
        try: return tuneMap[fieldName][propertyName]
        except KeyError:
            try: return self.tuneMap[fieldName][propertyName]
            except KeyError: return default

    def renderFields(self, object, formTuneMap):
        fieldOrder=self.getTuneMapItem(formTuneMap, "global", "fieldOrder", [])
        for fieldName, fieldType in self.fieldMap.items()+[("submit","submit")]:
            if "field "+fieldName not in fieldOrder:
                fieldOrder.append("field "+fieldName)
        res=""
        for fieldName in fieldOrder:
            if fieldName[:6]=="field ": res+=self.renderField(object, fieldName[6:], formTuneMap)
            else: res+=fieldName
        return res

    def renderField(self, object, fieldName, formTuneMap):
        if fieldName=="submit":
            label=self.getTuneMapItem(formTuneMap, fieldName, "label", fieldName)
            mask=self.getTuneMapItem(formTuneMap, fieldName, "mask", self.defaultFieldMask)
            extraArgMap=self.getTuneMapItem(formTuneMap, fieldName, "extraArgMap", {})
            return mask(*(label, "submit", "", "submit", "", "", extraArgMap))
        fieldType=self.fieldMap[fieldName]
        hidden=0
        if fieldType[-9:]==" linkBack":
            fieldType=fieldType[:-9]
            hidden=1
        if hasattr(object, fieldName): fieldValue=getattr(object, fieldName)
        else: fieldValue=None
        fieldValue=CherryObjects.encodeValue(fieldType, fieldValue)
        #print "Rendering field, fieldName:", fieldName, "encodedValue:", `fieldValue`
        label=self.getTuneMapItem(formTuneMap, fieldName, "label", fieldName)
        error=self.getTuneMapItem(formTuneMap, fieldName, "error", "")
        mask=self.getTuneMapItem(formTuneMap, fieldName, "mask", self.defaultFieldMask)
        optionList=[]
        if fieldType in ("string", "float"):
            typ="text"
        elif fieldType=="text":
            typ="textarea"
        elif fieldType=="boolean":
            typ="checkbox"
            optionList=[('1', '')]
        elif fieldType.find("link to ")==0:
            typ="select"
            objectName=fieldType.split()[-1].split('.')[0]
            optionList=globals()[objectName].getAllObjectsIdsAndLabels()
        elif fieldType.find("list of links to ")==0:
            typ="checkbox"
            objectName=fieldType.split()[-1].split('.')[0]
            optionList=globals()[objectName].getAllObjectsIdsAndLabels()
        else: raise "ERROR: fieldType not implemented: %s"%fieldType
        newOptionList=self.getTuneMapItem(formTuneMap, fieldName, "optionList", None)
        if newOptionList!=None:
            newOptionList=CherryObjects.encodeValue(fieldType, newOptionList)
            optionList=newOptionList
        extraArgMap=self.getTuneMapItem(formTuneMap, fieldName, "extraArgMap", {})
        if hidden: return self.hiddenMask('', fieldName, fieldValue, '', '', '', '')
        return mask(*(label, fieldName, fieldValue, typ, error, optionList, extraArgMap))
    def hiddenMask(self, label, name, fieldValue, typ, error, optionList, extraArgMap):
        if type(fieldValue)!=type([]): fieldValue=[fieldValue]
        res=""
        for fv in fieldValue:
            res+='<input type=hidden name="%s" value="%s">'%(name, fv)
        return res
    def displayMask(self, label, name, fieldValue, typ, error, optionList, extraArgMap):
        return '<input type=hidden name="%s" value="%s">%s %s<br>'%(name, fieldValue, label, fieldValue)
    def defaultFieldMask(self, label, name, fieldValue, typ, error, optionList, extraArgMap):
        res=label+' '
        if typ=='text':
            res+='<input name="%s" type=text value="%s">'%(name, fieldValue)
        if typ=='textarea':
            res+='<textarea name="%s" rows=10 cols=80>%s</textarea>'%(name, fieldValue)
        elif typ=='select':
            res+='<select name="%s">'%name
            for optionId, optionLabel in optionList:
                if optionId==fieldValue: res+="<option selected value=%s>%s</option>"%(optionId, optionLabel)
                else: res+="<option value=%s>%s</option>"%(optionId, optionLabel)
            res+='</select>'
        elif typ in ('checkbox','radio'):
            for optionId, optionLabel in optionList:
                res+='<input type="%s" name="%s" value="%s"'%(typ, name, optionId)
                if type(fieldValue)==type([]):
                    if optionId in fieldValue: res+=' checked'
                else:
                    if optionId==fieldValue: res+=' checked'
                res+='>&nbsp;&nbsp;%s<br>'%optionLabel
        elif typ=="submit":
            return "<input type=submit value='%s'>"%label
        if error:
            res+="&nbsp;<font color=red>"+error+"</font>"
        return res+"<br>"

    def displayValue(self, fieldType, value):
        i=fieldType.find(" linkBack")
        if i!=-1: fieldType=fieldType[:i]
        if fieldType in ("string", "text", "float"):
            if not value: return ''
            return tools.escapeHtml(str(value))
        elif fieldType=="boolean":
            if not value: return "False"
            return "True"
        elif fieldType.find("link to ")==0:
            if not value: return ""
            objectName=fieldType.split()[-1].split('.')[0]
            object=value
            try: evalLabel=globals()[objectName].tuneMap["global"]["label"]
            except KeyError: evalLabel="object.name"
            return "->"+eval(evalLabel)
        elif fieldType.find("list of links to ")==0:
            if not value: return []
            objectName=fieldType.split()[-1].split('.')[0]
            if type(value)!=type([]): value=[value]
            res=[]
            for item in value: res.append(self.displayValue("link to "+objectName, item))
            return res
        else: raise "ERROR: fieldType not implemented: %s"%fieldType

