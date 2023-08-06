# Copyright 2002-2004 CherryPy Team (team@cherrypy.org)
# 
# This program is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2, or (at your option) 
# any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program; if not, write to the Free Software 
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 
# 02111-1307, USA. 
# 
# As a special exception, the CherryPy team gives unlimited permission to 
# copy, distribute and modify the CherryPy scripts that are the 
# output of CherryPy.  You need not follow the terms of the GNU 
# General Public License when using or distributing such scripts, even 
# though portions of the text of CherryPy appear in them.  The GNU 
# General Public License (GPL) does govern all other use of the 
# material that constitutes the CherryPy program. 
# 
# Certain portions of the CherryPy source text are designed to be 
# copied (in certain cases, depending on the input) into the output of 
# CherryPy.  We call these the "data" portions.  The rest of the 
# CherryPY source text consists of comments plus executable code that 
# decides which of the data portions to output in any given case.  We 
# call these comments and executable code the "non-data" portions. 
# CherryPy never copies any of the non-data portions into its output. 
# 
# This special exception to the GPL applies to versions of CherryPy 
# released by the CherryPy team.  When you make and distribute a modified 
# version of CherryPy, you may extend this special exception to the 
# GPL to apply to your modified version as well, *unless* your 
# modified version has the potential to copy into its output some of 
# the text that was the non-data portion of the version that you 
# started with.  (In other words, unless your change moves or copies 
# text from the non-data portions to the data portions.)  If your 
# modification has such potential, you must delete any notice of this 
# special exception to the GPL from your modified version. 

################
CherryClass FormField abstract:
################
function:
    def __init__(self, label, name, typ, mask=None, mandatory=0, size=15, optionList=[], defaultValue='', defaultMessage='', validate=None):
        self.isField=1
        self.label=label
        self.name=name
        self.typ=typ
        if not mask: self.mask=defaultFormMask.defaultMask
        else: self.mask=mask
        self.mandatory=mandatory
        self.size=size
        self.optionList=optionList
        self.defaultValue=defaultValue
        self.defaultMessage=defaultMessage
        self.validate=validate
        self.errorMessage=""
    def render(self, leaveValues):
        if leaveValues:
            if self.typ!='submit':
                if request.paramMap.has_key(self.name): self.currentValue=request.paramMap[self.name]
                else: self.currentValue=""
            else: self.currentValue=self.defaultValue
        else:
            self.currentValue=self.defaultValue
            self.errorMessage=self.defaultMessage
        return self.mask(self)

################
CherryClass DefaultFormMask hidden:
################
view:
    def defaultMask(self, field):
        res="<tr><td valign=top>%s</td>"%field.label
        if field.typ=='text':
            res+='<td><input name="%s" type=text value="%s" size=%s></td>'%(field.name, field.currentValue, field.size)
        elif field.typ=='forced':
            res+='<td><input name="%s" type=hidden value="%s">%s</td>'%(field.name, field.currentValue, field.currentValue)
        elif field.typ=='password':
            res+='<td><input name="%s" type=password value="%s"></td>'%(field.name, field.currentValue)
        elif field.typ=='select':
            res+='<td><select name="%s">'%field.name
            for option in field.optionList:
                if type(option)==type(()):
                    optionId, optionLabel=option
                    if optionId==field.currentValue or str(optionId)==field.currentValue: res+="<option selected value=%s>%s</option>"%(optionId, optionLabel)
                    else: res+="<option value=%s>%s</option>"%(optionId, optionLabel)
                else:
                    if option==field.currentValue: res+="<option selected>%s</option>"%option
                    else: res+="<option>%s</option>"%option
            res+='</select></td>'
        elif field.typ=='textarea':
            # Size is colsxrows
            if field.size==15: size="15x15"
            else: size=field.size
            cols, rows=size.split('x')
            res+='<td><textarea name="%s" rows="%s" cols="%s">%s</textarea></td>'%(field.name, rows, cols, field.currentValue)
        elif field.typ=='submit':
            res+='<td><input type=submit value="%s"></td>'%field.name
        elif field.typ=='hidden':
            if type(field.currentValue)==type([]): currentValue=field.currentValue
            else: currentValue=[field.currentValue]
            res=""
            for value in currentValue:
                res+='<input name="%s" type=hidden value="%s">'%(field.name, value)
            return res
        elif field.typ=='checkbox' or field.typ=='radio':
            res+='<td>'
            # print "##### currentValue:", field.currentValue # TBC
            for option in field.optionList:
                if type(option)==type(()): optionValue, optionLabel=option
                else: optionValue, optionLabel=option, option
                res+='<input type="%s" name="%s" value="%s"'%(field.typ, field.name, optionValue)
                if type(field.currentValue)==type([]):
                    if optionValue in field.currentValue: res+=' checked'
                else:
                    if optionValue==field.currentValue: res+=' checked'
                res+='>&nbsp;&nbsp;%s<br>'%optionLabel
            res+='</td>'
        if field.errorMessage:
            res+="<td><font color=red>%s</font></td>"%field.errorMessage
        else:
            res+="<td>&nbsp;</td>"
        return res+"</tr>"
    def hiddenMask(self, field):
            if type(field.currentValue)==type([]): currentValue=field.currentValue
            else: currentValue=[field.currentValue]
            res=""
            for value in currentValue:
                res+='<input name="%s" type=hidden value="%s">'%(field.name, value)
            return res
    def defaultHeader(self, label):
        return "<table>"
    def defaultFooter(self, label):
        return "</table>"
    def echoMask(self, label):
        return label

################
CherryClass FormSeparator abstract:
################
function:
    def __init__(self, label, mask):
        self.isField=0
        self.label=label
        self.mask=mask
    def render(self, dummy):
        return self.mask(self.label)

################
CherryClass Form abstract:
################
variable:
    method="post"
    enctype=""
function:
    def formView(self, leaveValues=0):
        if self.enctype: enctypeTag='enctype="%s"'%self.enctype
        else: enctypeTag=""
        res='<form method="%s" %s action="%s/postForm">'%(self.method, enctypeTag, self.getPath())
        for field in self.fieldList:
            res+=field.render(leaveValues)
        return res+"</form>"
    def validateFields(self):
        # Should be subclassed
        # Update field's errorMessage value to set an error
        pass
    def validateForm(self):
        # Reset errorMesage for each field
        for field in self.fieldList:
            if field.isField: field.errorMessage=""

        # Validate mandatory fields
        for field in self.fieldList:
            if field.isField and field.mandatory and (not request.paramMap.has_key(field.name) or not request.paramMap[field.name]): field.errorMessage="Missing"

        # Validate fields one by one
        for field in self.fieldList:
            if field.isField and field.validate and not field.errorMessage:
                if request.paramMap.has_key(field.name): value=request.paramMap[field.name]
                else: value=""
                field.errorMessage=field.validate(value)

        # Validate all fields together (ie: check that passwords match)
        self.validateFields()
        for field in self.fieldList:
            if field.isField and field.errorMessage: return 0
        return 1
    def setFieldErrorMessage(self, fieldName, errorMessage):
        for field in self.fieldList:
            if field.isField and field.name==fieldName: field.errorMessage=errorMessage
    def getFieldOptionList(self, fieldName):
        for field in self.fieldList:
            if field.isField and field.name==fieldName: return field.optionList
    def getFieldDefaultValue(self, fieldName):
        for field in self.fieldList:
            if field.isField and field.name==fieldName: return field.defaultValue
    def setFieldDefaultValue(self, fieldName, defaultValue):
        for field in self.fieldList:
            if field.isField and field.name==fieldName: field.defaultValue=defaultValue

    def getFieldNameList(self, exceptList=[]):
        fieldNameList=[]
        for field in self.fieldList:
            if field.isField and field.name and field.name not in exceptList: fieldNameList.append(field.name)
        return fieldNameList


