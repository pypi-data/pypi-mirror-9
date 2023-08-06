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
CherryClass AspClass:
aspect:
    (dummy):
        pass
"""
compilerErrorList1=["Wrong aspect header"]

config2="""
[server]
logFile=logFile
logToScreen=0
"""
code2="""
from UserDict import UserDict
CherryClass AspClass:
aspect:
    (method.name == 'index') start:
        _page.append("name works")
    (method.className == 'MyClass') start:
        _page.append("className works")
    (method.isHidden) start:
        _page.append("isHidden works")
    (method.type == 'mask') end:
        _page.append("type works")
CherryClass Root(AspClass):
mask:
    def index(self):
        Hi
    def index2(self) hidden:
        Hi
view:
    def index3(self):
        return self.index2()
CherryClass MyClass(AspClass):
mask:
    def index(self):
        Hi
CherryClass Level2(Root):
mask:
    def index(self):
        Hi2
# Check that it doesn't think that UserDict is a CherryClass ...
CherryClass Dummy(AspClass,UserDict):
mask:
    def index(self):
        OK

# Example from Mario that was failing in 0.9-gamma
CherryClass SubBase abstract:
aspect:
    (1) start:
        _page.append('hey you!')
CherryClass Base(SubBase) abstract:
aspect:
    (2) end:
        _page.append('see ya later!')
CherryClass Final(Base):
mask:
    def index(self):
        how you doin?

# Test nested aspect classes by multiple inheritance
CherryClass Nest1:
aspect:
    (1) start:
        _page.append('nest1head ')
    (1) end:
        _page.append('nest1foot ')

CherryClass Nest2:
aspect:
    (1) start:
        _page.append('nest2head ')
    (1) end:
        _page.append('nest2foot ')

CherryClass Nest(Nest1, Nest2):
mask:
    def index(self):
        Hello

# Test nested aspect classes by 2-level inheritance
CherryClass Aspect_A:
aspect:
    (method.type=='mask') start:
        _page.append('''
        <html>
        <body>
        ''')

    (method.type=='mask') end:
        _page.append('''
        </body>
        </html>
        ''')


CherryClass Aspect_B:
aspect:
    (method.type=='mask') start:
        _page.append('''
        <div>
        ''')

    (method.type=='mask') end:
        _page.append('''
        </div>
        ''')

CherryClass A(Aspect_A):
mask:
    def index(self):
        <p>Hello, World-A!</p>

CherryClass B(A, Aspect_B):
mask:
    def index(self):
        <p>Hello, World-B!</p>

"""
urlList2 = ["", "index3", "myClass/index", "level2", "final", "nest", "b"]
expectedResultList2 = ["name worksHi\ntype works", "isHidden worksHi\ntype works", "name worksclassName worksHi\ntype works", "name worksHi2\ntype works", "hey you!how you doin?\nsee ya later!", "nest1head nest2head Hello\nnest2foot nest1foot ", "\n        <html>\n        <body>\n        \n        <div>\n        <p>Hello, World-B!</p>\n\n        </div>\n        \n        </body>\n        </html>\n        "]

def test(infoMap, failedList, skipped):
    print "    Testing aspect classes..."
    print "        (1)...",
    # Test that the compiler returns the correct error is an aspect header in not right
    testCode.checkInCompilerError("Aspect (1)", infoMap, code1, "", compilerErrorList1, failedList)
    print "        (2)...",
    testCode.checkPageResult("Aspect (2)", infoMap, code2, config2, "", urlList2, expectedResultList2, failedList)

