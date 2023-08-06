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

# Test if XML-RPC works
code="""
CherryClass Root:
view:
    def add(self, a, b, c) xmlrpc:
        # Return the sum of three numbers
        return a+b+c

CherryClass Xml_rpc:
view:
    def reverse(self, label) xmlrpc:
        # Reverse the characters of a string
        newStr=''
        for i in range(len(label)-1,-1,-1):
            newStr+=label[i]
        return newStr
CherryClass Normal:
mask:
    def index(self):
        OK
"""
config="""
[server]
logFile=logFile
logToScreen=0
typeOfRequests=xmlRpc,web
"""

config2="""
[server]
logFile=logFile
logToScreen=0
typeOfRequests=xmlRpc,web
sslKeyFile=server.pkey
sslCertificateFile=server.cert
"""

urlList=["", "", "xml"]
funcList=["add(1,2,3)", "xml.rpc.reverse('I love CherryPy')", "rpc.reverse('I love CherryPy')"]
expectedResultList=[6, 'yPyrrehC evol I', 'yPyrrehC evol I']

urlList2=["normal"]
expectedResultList2=["OK\n"]

def test(infoMap, failedList, skippedList):
    print "    Testing XML-RPC...",
    haveXmlrpclib=1
    try: import xmlrpclib
    except: haveXmlrpclib=0
    if not haveXmlrpclib or not infoMap['hasXmlrpclib']:
        print "skipped"
        skippedList.append("XML-RPC for python%s"%infoMap['exactVersionShort']+": xmlrpclib module not available")
        return

    print "\n        (1)...",
    testCode.checkXmlrpcResult("XML-RPC (1)", infoMap, code, config, "", urlList, funcList, expectedResultList, failedList)
    print "        (2)...",
    testCode.checkPageResult("XML-RPC (2)", infoMap, code, config, "", urlList2, expectedResultList2, failedList)
    print "        (3)...",
    import socket
    if not hasattr(socket, "ssl"):
        print "skipped"
        skippedList.append("XML-RPC/SSL for python%s"%infoMap['exactVersionShort']+": python is not ssl-enabled")
        return
    if not infoMap['hasPyOpenSSL']:
        print "skipped"
        skippedList.append("XML-RPC/SSL for python%s"%infoMap['exactVersionShort']+": PyOpenSSL module not available")
        return
    testCode.checkPageResult("XML-RPC (3)", infoMap, code, config2, "", urlList2, expectedResultList2, failedList, isSSL=1)

