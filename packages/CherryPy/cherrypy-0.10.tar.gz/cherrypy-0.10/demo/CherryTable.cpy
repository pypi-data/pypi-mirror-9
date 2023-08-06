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

#############################################
#
# WARNING: This module was experimental code and
# is not longer maintained or used (except
# in the Prestation demo)
#
# DO NOT USE IT FOR REAL STUFF
#
#############################################

import types

def initServer():
    # We have to put this in initServer, because all the tables have to be instantiated before we read the database file
    cherryDb.databaseRead()

######################
CherryClass CherryDb:
######################
function:
    def databaseWrite(self, table, action, where, kw):
        f=open('database','a')
        param=","
        if where!=None: param+="%s,"%`where`
        for key, value in kw.items():
            if key!='_id': param+="%s=%s,"%(key, `value`)
        param+="_rd=1,"
        f.write('%s.%s(%s)\n'%(table, action, param[1:-1]))
        f.close()
    def databaseRead(self):
        try:
            f=open(configFile.get('prestationDatabase','file'),'r')
            logMessage("Reading gaz station database for the Prestation demo ...")
            data=f.read()
            f.close()
        except:
            logMessage("No database found")
            return
        data=data.replace('\r\n','\n')
        lines=data.split('\n')
        i=0
        while i<len(lines):
            cmd=lines[i]
            if not cmd: break
            if cmd[-1]!=')': logMessage("Warning, database file is corrupt line %s (last char:%s)"%(i,`cmd[-1]`))
            else: exec(cmd)
            i+=1
        logMessage("Done reading database")

    # Function to get an item from its representation
    def getInstanceItem(self, instanceItem):
        i=instanceItem.rfind("_")
        table=instanceItem[10:i]
        id=instanceItem[i+1:]
        instanceList=eval(table+".getItem('item._id=='+id)")
        return instanceList[0]

    def getToken(self, str):
        if str[0]=='"':
            end=findClosingQuote(str, '"', 1)
            return str[:end+1]
        elif str[0]=='"':
            end=findClosingQuote(str, "'", 1)
            return str[:end+1]
        else:
            j=str.find(" ")
            if j==-1: j=len(str)
            k=str.find(")")
            if k==-1: k=len(str)
            i=min([j,k])
            return str[:i]




######################
CherryClass CherryDbItem abstract:
######################
function:
    def __init__(self, _id, _tableName):
        self._id=_id
        self._tableName=_tableName
    def __repr__(self):
        return '"_instance_%s_%s"'%(self._tableName, self._id)


######################
CherryClass CherryTable abstract:
######################
aspect:
    method.name=='__init__' start:
        self._id=0
        self._itemList=[]
        self._indexMap={}
        self.column=[]
        self.specialColumn=[]
        self.index=[]
        self.specialIndex=[]
        self._tableName=self.__class__.__name__
        self._tableName=self._tableName[0].lower()+self._tableName[1:]
    method.name=='__init__' end:
        self.index.append('_id')
        for index in self.index:
            self._indexMap[index]={}
        for index in self.specialIndex:
            value, as=index.split(" as ")
            self._indexMap[as]={}

function:
    def addItem(self, **kw):
        if kw.has_key("_id"):
            _id=kw["_id"]
            if _id>self._id: self._id=_id
        else:
            self._id+=1
            _id=self._id
        # Check for "_instance_"
        for _key, _value in kw.items():
            if type(_value)==types.StringType and _value[:10]=="_instance_":
                instance=cherryDb.getInstanceItem(_value)
                kw[_key]=instance
        item=CherryDbItem(self._id, self._tableName)
        if not kw.has_key("_rd"): cherryDb.databaseWrite(item._tableName, "addItem", None, kw)
        self._itemList.append(item)
        # Add columns, special columns and index item
        for column in self.column:
            if kw.has_key(column): exec("item.%s=kw[column]"%column)
            else: exec("item.%s=None"%column)
        for specialColumn in self.specialColumn:
            _valueStr, as=specialColumn.split(" as ")
            _value=eval(_valueStr)
            exec("item.%s=_value"%as)
        self._indexItem(item)
        return item

    def getItem(self, where="", sortBy="", order="asc", firstValueList=[], lastValueList=[None]):
        # Work on where clause: replace all occurences of "instance_table_id" with actual item
        tmpInstanceList=[]
        tmpInstanceId=0
        while 1:
            i=where.find('"_instance_')
            if i==-1: break
            k=where.find('"', i+1)
            tmpInstance=cherryDb.getInstanceItem(where[i+1:k])
            tmpInstanceList.append(tmpInstance)
            where=where[:i]+"tmpInstanceList[%s]"%tmpInstanceId+where[k+1:]
            tmpInstanceId+=1
        # Check for indexes (only if "or" and "not" are not used
        itemLoopList=self._itemList
        if where.find(" or ")==-1 and where.find(" not ")==-1:
            for index in self.index+self.specialIndex:
                # Check if it's a special index
                sp=index.split(" as ")
                if len(sp)==2: index=sp[1]
                i=where.find("item.%s=="%index)
                if i!=-1:
                    token=cherryDb.getToken(where[i+7+len(index):])
                    value=eval(token)
                    if not self._indexMap[index].has_key(value): return []
                    itemLoopList=self._indexMap[index][value]
                    where=where[:i]+where[i+7+len(index)+len(token):]
        if not where: return itemLoopList
        res=[]
        for item in itemLoopList:
            if eval(where): res.append(item)
        if sortBy:
            # Sort results
            tmpRes, firstValueRes, lastValueRes=[], [], []
            for item in res:
                field=eval("item.%s"%sortBy)
                if field in firstValueList: firstValueRes.append(item)
                if field in lastValueList: lastValueRes.append(item)
                else: tmpRes.append((field, item))
                tmpRes.sort()
            if order=="desc": tmpRes.reverse()
            res=firstValueRes
            for field, item in tmpRes: res.append(item)
            res+=lastValueRes
        return res

    # Function to add item to indexes
    def _indexItem(self, item):
        for index in self.index:
            value=eval("item.%s"%index)
            if self._indexMap[index].has_key(value): self._indexMap[index][value].append(item)
            else: self._indexMap[index][value]=[item]
        for index in self.specialIndex:
            valueStr, as=index.split(" as ")
            value=eval(valueStr)
            if type(value)!=types.ListType: value=[value]
            for val in value:
                if self._indexMap[as].has_key(val): self._indexMap[as][val].append(item)
                else: self._indexMap[as][val]=[item]

    # Function to remove item from indexes
    def _unIndexItem(self, item):
        for index in self.index:
            value=eval("item.%s"%index)
            self._indexMap[index][value].remove(item)

    def deleteItem(self, whereOrItemList="", **kw):
        itemList=self._getWhereOrItemList(whereOrItemList)[:]
        if itemList:
            for item in itemList:
                self._itemList.remove(item)
                self._unIndexItem(item)
            if not kw.has_key("_rd"): cherryDb.databaseWrite(itemList[0]._tableName, "deleteItem", itemList, kw)

    def updateItem(self, whereOrItemList="", **kw):
        itemList=self._getWhereOrItemList(whereOrItemList)[:]
        if itemList:
            for item in itemList:
                self._unIndexItem(item)
                for _key in kw.keys():
                    exec('item.%s=kw["%s"]'%(_key,_key))
                self._indexItem(item)
            if not kw.has_key("_rd"): cherryDb.databaseWrite(itemList[0]._tableName, "updateItem", itemList, kw)

    # Function to return a list of item for a given whereOrItemList
    def _getWhereOrItemList(self, whereOrItemList):
        if type(whereOrItemList)==types.StringType: return self.getItem(whereOrItemList)
        else:
            itemList=[]
            for item in whereOrItemList:
                if type(item)==types.StringType and item[:10]=="_instance_":
                    item=cherryDb.getInstanceItem(item)
                    itemList.append(item)
                else: itemList.append(item)
            return itemList

