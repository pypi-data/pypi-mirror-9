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
    def index(self, name="World"):
        before<py-include="template.html">after
        before<div py-include="template.html"></div>after
"""
code2="""
CherryClass Root:
mask:
    def index(self, name="World"):
        <py-include="template2.html">
"""
code3="""
CherryClass Root:
mask:
    def index(self, name="World"):
        <py-include="template.html">
        <py-eval "name">
"""
config="""
[server]
logFile=logFile
logToScreen=0
"""
expectedResult='before<html><body>\n    Hello, World\n    \n        OK\n    \n</body></html>\nafter\nbefore<html><body>\n    Hello, World\n    \n        OK\n    \n</body></html>\nafter\n'

expectedErrorList2=["""Tag 'py-eval' should be followed by '="'""", "in File 'template2.html', in CherryClass 'Root', in function 'index'"]
expectedErrorList3=["""Tag 'py-eval' should be followed by '="'""", "in File 'Root.cpy', in CherryClass 'Root', in function 'index'"]

def test(infoMap, failedList, skippedList):
    print "    Testing py-include..."
    print "        (1)...",
    testCode.checkPageResult("py-include (1)", infoMap, code, config, "", [""], [expectedResult], failedList)
    print "        (2)...",
    testCode.checkInCompilerError("py-include (2)", infoMap, code2, "", expectedErrorList2, failedList)
    print "        (3)...",
    testCode.checkInCompilerError("py-include (3)", infoMap, code3, "", expectedErrorList3, failedList)
