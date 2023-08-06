use Tools

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
CherryClass MaskTools:
################
view:
    def xData(self):
        # Return a gif image with a single transparent pixel
        response.headerMap['content-type']='image/gif'
        return 'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
function:
    def x(self):
        return '<img src="%s/xData" width=1 height=1>'%self.getPath()
    def displayByColumn(self, dataList, numberOfColumns=2, columnWidth=0, gapWidth=50, tdClass=''):
        numberOfItems=len(dataList)
        itemsPerColumn=numberOfItems/numberOfColumns
        if numberOfColumns*itemsPerColumn<numberOfItems: itemsPerColumn+=1

        res="<table border=0 cellspacing=0 cellpadding=0><tr>"
        for i in range(numberOfColumns):
            res+="<td valign=top %s %s>"%(tools.getAttribute('width', columnWidth), tools.getAttribute('class', tdClass))
            for data in dataList[i*itemsPerColumn:(i+1)*itemsPerColumn]:
                res+=data+'<br>'
            res+="</td>"
            if gapWidth and i!=numberOfColumns-1: res+="<td width=%s>%s</td>"%(gapWidth, self.x())
        res+="</tr></table>"
        return res

    def displayByLine(self, dataList, numberOfLines=2, lineHeight=0, gapHeight=50, tdClass=''):
        numberOfItems=len(dataList)
        itemsPerLine=numberOfItems/numberOfLines
        if numberOfLines*itemsPerLine<numberOfItems: itemsPerLine+=1

        res="<table border=0 cellspacing=0 cellpadding=0>"
        for i in range(numberOfLines):
            res+="<tr><td align=left %s %s>"%(tools.getAttribute('height', lineHeight), tools.getAttribute('class', tdClass))
            for data in dataList[i*itemsPerLine:(i+1)*itemsPerLine]:
                res+=data+' '
            res+="</td></tr>"
            if gapHeight and i!=numberOfLines-1: res+="<tr><td height=%s>%s</td></tr>"%(gapHeight, self.x())
        res+="</table>"
        return res

mask:
    def textInBox(self, text, boxColor="black", insideColor="white"):
        <table border=0 cellspacing=0 cellpadding=1><tr><td py-attr="boxColor" bgColor="">
            <table border=0 cellspacing=0 cellpadding=5><tr><td py-attr="insideColor" bgColor="" py-eval="text">
            </td></tr></table>
        </td></tr></table>


function:
    def sortedKeys(self,map):
        keys = map.keys()
        keys.sort() 
        return keys

mask:
    def prettyMap(self, aMap, label=None, isRecursiveCall=0):
         <py-if="not isRecursiveCall">
         <style>
         .prettyMap { background-color:#ccc; }
         .prettyMapHead { background-color:#fcc; }
         .prettyMapKeys { background-color:#eee; }
         .prettyMapValues { background-color:#fff; }
         .prettyMapSubMap { background-color:#fcc; }
         </style>
         </py-if>
         <table width="100%" border="0" cellspacing="1" cellpadding="3" class="prettyMap">
             <py-if="label is not None">
            <tr width="100%" valign="top" align="left">
                <th align="left" colspan="2" width="100%" class="prettyMapHead">
                    <py-eval="label">
                </th>
            </tr>
            </py-if>
            <py-for="key in self.sortedKeys(aMap)">
            <tr width="100%" valign="top" align="left" class="prettyMapValues">
                <td width="20%" class="prettyMapKeys"><py-eval="key"></td>
                <py-if="type(aMap[key])==types.DictType">
                <td width="80%" class="prettyMapSubMap">
                    <py-eval="self.prettyMap(aMap[key],isRecursiveCall=1)">
                </td>
                </py-if>
                <py-else>
                <td width="80%"><py-eval="aMap[key]"></td>
                </py-else>
            </tr>
            </py-for>
        </table>
