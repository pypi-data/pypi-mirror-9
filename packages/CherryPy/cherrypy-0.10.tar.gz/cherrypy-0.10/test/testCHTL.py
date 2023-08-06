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
        <b py-eval="2*2"></b>
        <div py-eval="name"></div>
        <a py-attr="'myLink'" href="">link</a>
        <a py-attr="'%sLink'%name" href="">linkWorld</a>
        <div py-exec="a=2"></div><u py-eval=a></u>
        <div py-code="
            a+=1
            a+=2
        "></div><span py-eval="a"></span>
        <div py-code="
        a+=1
        a+=2
        "></div><span py-eval="a"></span>
        <div py-code="
            a+=1
            a+=2
        "></div><span py-eval="a"></span>
        <div py-if="1==1">ok</div>
        <div py-if="1==0">not ok</div>
        <div py-else>ok</div>
        <div py-for="a,b in [(0,0), (1,1), (0,1)]">
            <div py-eval="a+b"></div>
        </div>
        <div py-for="i in range(3)">
            <div py-eval="'%s,2 == %s,%s'%(i,_index,_end)"></div>
            <div py-for="j in range(2)">
                <div py-eval="'%s,1 == %s,%s'%(j,_index,_end)"></div>
                <div py-for="k in range(3)">
                    <div py-eval="'%s,2 == %s,%s'%(k, _index,_end)"></div>
                </div>
                <div py-eval="'%s,1 == %s,%s'%(j,_index,_end)"></div>
            </div>
            <div py-eval="'%s,2 == %s,%s'%(i,_index,_end)"></div>
        </div>
        \""" \""" '''
        <div py-code="
            a = "OK"
            _page.append(a)
        "></div>
        <div py-exec="a = 'OK1 \\"OK2\\" OK3'"></div>
        <div py-eval="a"></div>
        <div py-eval="'py-eval 1'"></div>
        <div py-eval="'py-eval 2'"></div>
        <div py-code="
            a = 'py-code 1'
            _page.append(a)
        "></div>

"""
config="""
[server]
logFile=logFile
logToScreen=0
"""
expectedResult='<b>4</b>\nworld\n<a href="myLink">link</a>\n<a href="worldLink">linkWorld</a>\n<u py-eval=a></u>\n<span>5</span>\n<span>8</span>\n<span>11</span>\nok\nok\n\n    0\n\n    2\n\n    1\n\n\n    0,2 == 0,2\n    \n        0,1 == 0,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        0,1 == 0,1\n    \n        1,1 == 1,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        1,1 == 1,1\n    \n    0,2 == 0,2\n\n    1,2 == 1,2\n    \n        0,1 == 0,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        0,1 == 0,1\n    \n        1,1 == 1,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        1,1 == 1,1\n    \n    1,2 == 1,2\n\n    2,2 == 2,2\n    \n        0,1 == 0,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        0,1 == 0,1\n    \n        1,1 == 1,1\n        \n            0,2 == 0,2\n        \n            1,2 == 1,2\n        \n            2,2 == 2,2\n        \n        1,1 == 1,1\n    \n    2,2 == 2,2\n\n""" """ \'\'\'\nOK\n\nOK1 "OK2" OK3\npy-eval 1\npy-eval 2\npy-code 1\n'

def test(infoMap, failedList, skippedList):
    print "    Testing CHTL...",
    testCode.checkPageResult("CHTL", infoMap, code, config, "", [""], [expectedResult], failedList)


