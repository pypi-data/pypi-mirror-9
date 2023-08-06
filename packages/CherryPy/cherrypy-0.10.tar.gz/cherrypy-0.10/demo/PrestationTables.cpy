use CherryTable

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


######################
CherryClass StationTable(CherryTable):
######################
function:
    def __init__(self):
        self.column=['name','zipCode','city','address','phone','open','type','super','sp95','sp98','gazole','gerant','lastUpdateTime']
        self.specialColumn=['item.zipCode[:2] as department', 'item.name.upper()+" "+item.city.upper()+" "+item.address.upper()+" "+item.open.upper() as keyWord']
    def getAllTypes(self):
        typeList=[]
        stationList=self.getItem()
        for station in stationList:
            if station.type not in typeList: typeList.append(station.type)
        typeList.sort()
        return typeList

######################
CherryClass NewInfoTable(CherryTable):
######################
function:
    def __init__(self):
        self.column=['station','name','zipCode','city','address','phone','open','type','nameOrEmail','lastUpdateTime']

######################
CherryClass NewPriceTable(CherryTable):
######################
function:
    def __init__(self):
        self.column=['station','super','sp95','sp98','gazole','nameOrEmail','lastUpdateTime']

######################
CherryClass CommentTable(CherryTable):
######################
function:
    def __init__(self):
        self.column=['station','comment','nameOrEmail','checked','lastUpdateTime']

######################
CherryClass NewStationTable(CherryTable):
######################
function:
    def __init__(self):
        self.column=['name','zipCode','city','address','phone','open','type','super','sp95','sp98','gazole','gerant','nameOrEmail','lastUpdateTime']

######################
CherryClass RequestTable(CherryTable):
######################
function:
    def __init__(self):
        self.column=['name','lastUpdateTime']

##############
CherryClass ViewTables:
##############
function:
    def getTableData(self, tableName):
        # Return columnList, recordList
        # recordList is a list of recordData
        # and recordData is a list of double (data, link)
        table=eval(tableName)
        columnList=table._column
        recordList=[]
        i=0
        for item in table.getItem():
            i+=1
            recordData=[]
            for column in columnList:
                columnValue=eval('item.%s'%column)
                recordData.append((columnValue, None))
            recordList.append(recordData)
        indexMap=eval('%s._indexMap'%tableName)
        return tableName, columnList, recordList, indexMap

mask:
    def viewTables(self):
        <html><body>
            <table border=1><tr><th>Table</th></tr>
            <div py-for="tableName in ['station']">
                <tr><td><a py-attr="request.base+'/viewTables/viewTable?tableName='+tableName" href="#" py-eval="tableName">table</a></td></tr>
            </div>
            </table>
        </body></html>
    def viewTableMask(self, tableName, columnList, recordList, indexMap):
        <html><body>
            <b>Data for table: <div py-eval="tableName"></div><br><br></b>
            <table border=1>
                <tr><div py-for="column in columnList"><th py-eval="column"></th></div></tr>
                <div py-for="recordData in recordList"><tr>
                    <div py-for="columnValue, columnLink in recordData">
                        <td py-eval="columnValue">Value</td>
                    </div>
                </tr></div>
            </table>
            <br>
            <b>IndexMap:</b><br>
            <div py-for="key,value in indexMap.items()">
                <div py-eval="'<b>%s'%key+':</b>'+'%s'%value+'<br>'">key, value</div>
            </div>
        </body></html>

    def testForMask(self):
        <div py-for="i in range(10)">
            i:<div py-eval="i">i</div>
        </div>

view:
    def viewTable(self, tableName):
        return apply(self.viewTableMask, self.getTableData(tableName))


