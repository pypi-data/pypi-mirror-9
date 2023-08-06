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

code1="""
CherryClass Root:
mask:
-TAB-def index(self):
-TAB--TAB-Test code that uses tabs
-TAB--TAB-<py-exec="a=1">
-TAB--TAB-<div py-code="
-TAB--TAB--TAB-if a == 1: a += 1
-TAB--TAB--TAB-"></div>
-TAB--TAB-<div py-eval="a">This is a</div>
"""

code2="""
CherryClass Root:
mask:
   def index(self):
      Test code that uses 3 spaces for indentation
      <py-exec="a=1">
      <div py-code="
         if a == 1: a += 1
            "></div>
               <div py-eval="a">This is a</div>
"""

code3="""
CherryClass Root:
mask:
     def index(self):
-TAB-     Test code that uses a mix of tabs and 5 spaces for indentation
     -TAB-<py-exec="a=1">
          <div py-code="
-TAB--TAB-if a == 1: a += 1
          "></div>
-TAB-     -TAB-<div py-eval="a">This is a</div>
"""


config="""
[staticContent]
static=static
[server]
logFile=logFile
logToScreen=0
"""
urlList = ['index']
expectedResultList1 = ['Test code that uses tabs\n\n\n2\n']
expectedResultList2 = ['Test code that uses 3 spaces for indentation\n\n\n            2\n']
expectedResultList3 = ['Test code that uses a mix of tabs and 5 spaces for indentation\n\n\n    2\n']

def test(infoMap, failedList, skippedList):
    print "    Testing indentation ..."
    print "        (1)...",
    # Test code with tabs
    testCode.checkPageResult("Indentation", infoMap, code1.replace('-TAB-', '\t'), config, "", urlList, expectedResultList1, failedList)
    print "        (2)...",
    # Test code that uses 3 spaces for indentation
    testCode.checkPageResult("Indentation", infoMap, code2, config, "-W 3", urlList, expectedResultList2, failedList)
    print "        (3)...",
    # Test code that uses 3 spaces for indentation
    testCode.checkPageResult("Indentation", infoMap, code3.replace('-TAB-', '\t'), config, "-W 5", urlList, expectedResultList3, failedList)


