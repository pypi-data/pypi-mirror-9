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

# Test that hidden inheritance works correctly
code1="""
CherryClass A hidden:
mask:
    def header(self):
        header
    def footer(self):
        footer
    def other1(self):
        other1
    def other2(self):
        other2
CherryClass B(A):
mask:
    def index(self):
        <py-eval="self.header()">
        index
        <py-eval="self.footer()">
    def other1(self):
        other1
        <py-eval="a.other1()">
    def other2(self) hidden:
        other2
        <py-eval="b.other2()">
    def new(self):
        new

CherryClass C abstract:
mask:
    def header(self) hidden:
        header

CherryClass D(C):
mask:
    def index(self):
        <py-eval="self.header()">
"""

config1="""
[server]
logFile=logFile
logToScreen=0
"""

urlList=["b/index", "b/other1", "b/new"]
expectedResultList=['header\n\nindex\nfooter\n\n', 'other1\nother1\n\n', 'new\n']

hiddenUrlList=["a/header", "b/header", "b/other2", "d/header"]
expectedHiddenResultList=[
    'CherryError: couldn\'t map URL to an existing non-hidden mask or view (tried "a.header" and "a_header.index")',
    'CherryError: couldn\'t map URL to an existing non-hidden mask or view (tried "b.header" and "b_header.index")',
    'CherryError: couldn\'t map URL to an existing non-hidden mask or view (tried "b.other2" and "b_other2.index")',
    'CherryError: couldn\'t map URL to an existing non-hidden mask or view (tried "d.header" and "d_header.index")',
    ]

def test(infoMap, failedList, skipped):
    print "    Testing hidden class masks non-availability..."
    print "        (1)....",
    testCode.checkPageResult("Hidden class (1)", infoMap, code1, config1, "", urlList, expectedResultList, failedList)
    print "        (2)....",
    testCode.checkPageResult("Hidden class (2)", infoMap, code1, config1, "", hiddenUrlList, expectedHiddenResultList, failedList, 0)

