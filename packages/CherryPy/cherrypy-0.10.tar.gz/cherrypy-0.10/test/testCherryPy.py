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

# Regression test suite for CherryPy

python2={}
python2[1]={}    # Infos about python-2.1
python2[2]={}    # Infos about python-2.2
python2[3]={}    # Infos about python-2.3

# Edit these lines to match your setup
import sys
if sys.platform=="win32":
    python2[1]['path']="c:\\python21\\python"
    python2[2]['path']="c:\\python22\\python"
    python2[3]['path']="c:\\python23\\python"
else:
    python2[1]['path']="python2.1"
    python2[2]['path']="python2.2"
    python2[3]['path']="python2.3"

testList=[
    "testCGTL",
    "testCHTL",
    "testUrlMethodMapping",
    "testIndentation",
    "testSpecialInputFiles",
    "testAbstract",
    "testHidden",
    "testAspect",
    "testHttpAuthenticate",
    "testXmlrpc",
    "testSession",
    "testSSL",
    "testStaticContent",
    "testPyInclude",
    "testHotReload",
    "testMultipleSections",
    ]

#testList = ["testAspect"] # TBC

print "Checking that port 8000 is free...",
try:
    import socket
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 8000))
    s.close()
    print "\n### Error: port 8000 is busy. This port must be free to run this test script"
    sys.exit(-1)
except socket.error: print "OK"

print

print "Examining your system..."
print
print "Python version used to run this test script:", sys.version.split()[0]
print
import buildInfoMap
python2=buildInfoMap.buildInfoMap(python2)

print
print "Checking CherryPy version..."
import os
v=python2.keys()[0]
path=python2[v]['path']
version=os.popen("%s ../cherrypy.py -V"%path).read().strip()
if not version:
    print "Error: couln't find CherryPy !"
    os._exit(-1)
print "    Found version "+`version`
print

print "Testing CherryPy..."
failedList=[]
skippedList=[]

for version, infoMap in python2.items():
    print "Running tests for python %s..."%infoMap['exactVersionShort']
    for test in testList:
        exec("import "+test)
        eval(test+".test(infoMap, failedList, skippedList)")


print
print
print "#####################################"
print "#####################################"
print "###          TEST RESULT          ###"
print "#####################################"
print "#####################################"
if skippedList:
    print
    print "*** THE FOLLOWING TESTS WERE SKIPPED:"
    for skipped in skippedList: print skipped

    print "**** THE ABOVE TESTS WERE SKIPPED"
    print

if failedList:
    print
    print "*** THE FOLLOWING TESTS FAILED:"
    for failed in failedList: print failed

    print "**** THE ABOVE TESTS FAILED"
    print
    print "**** Some errors occured: please send an e-mail to remi@cherrypy.org with the output of this test script"

else:
    print
    print "**** NO TEST FAILED: EVERYTHING LOOKS OK ****"

############"
# Ideas for future tests:
#    - test if tabs and whitespaces are handled correctly in source file (option -W)
#    - test if absolute pathnames work fine on windows
#    - test sessions
#    - test threading server
#    - test forking server
#    - test process pooling server
#    - test SSL
#    - test compilator errors
#    - test abstract classes
#    - test hidden classes
#    ...

