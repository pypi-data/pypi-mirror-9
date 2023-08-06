# Copyright 2002-2003 CherryPy Team (team@cherrypy.org)
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

import testCode

code="""
CherryClass Root:
mask:
    def index(self, name="world"):
        <py-eval="2*2">
        <py-eval="name">
        <py-exec="a=2"><u py-eval="a"></u>
        <py-code="
            a+=1
            a+=2
        "><py-eval="a">
        <py-code="
        a+=1
        a+=2
        "><py-eval="a">
        <py-code="
            a+=1
            a+=2
        "><py-eval="a">
        <py-if="1==1">ok</py-if>
        <py-if="1==0">not ok</py-if>
        <py-else>ok</py-else>
        <py-for="a,b in [(0,0), (1,1), (0,1)]">
            <div py-eval="a+b"></div>
        </py-for>
        <py-for="i in range(3)">
            <py-eval="'%s,2 == %s,%s'%(i,_index,_end)">
            <py-for="j in range(2)">
                <py-eval="'%s,1 == %s,%s'%(j,_index,_end)">
                <py-for="k in range(3)">
                    <py-eval="'%s,2 == %s,%s'%(k, _index,_end)">
                </py-for>
                <py-eval="'%s,1 == %s,%s'%(j,_index,_end)">
            </py-for>
            <py-eval="'%s,2 == %s,%s'%(i,_index,_end)">
        </py-for>
        \""" \""" '''
        <py-code="
            a = "OK"
            _page.append(a)
        ">
        <py-exec="a = 'OK1 \\"OK2\\" OK3'">
        <py-eval="a">
        <py-eval="'py-eval 1'"/>
        <py-eval="'py-eval 2'" />
        <py-code="
            a = 'py-code 1'
            _page.append(a)
        "/>
"""
config="""
[server]
logFile=logFile
logToScreen=0
"""
expectedResult='4\nworld\n<u>2</u>\n5\n8\n11\nok\nok\n\n    0\n\n    2\n\n    1\n\n\n    0,2 == 0,2\n    \n        0,1 == 0,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        0,1 == 0,1\n    \n        1,1 == 1,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        1,1 == 1,1\n    \n    0,2 == 0,2\n\n    1,2 == 1,2\n    \n        0,1 == 0,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        0,1 == 0,1\n    \n        1,1 == 1,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        1,1 == 1,1\n    \n    1,2 == 1,2\n\n    2,2 == 2,2\n    \n        0,1 == 0,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        0,1 == 0,1\n    \n        1,1 == 1,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        1,1 == 1,1\n    \n    2,2 == 2,2\n\n""" """ \'\'\'\nOK\n\nOK1 "OK2" OK3\npy-eval 1\npy-eval 2\npy-code 1\n'

def test(infoMap, failedList, skippedList):
    print "    Testing CGTL...",
    testCode.checkPageResult("CGTL", infoMap, code, config, "", [""], [expectedResult], failedList)
