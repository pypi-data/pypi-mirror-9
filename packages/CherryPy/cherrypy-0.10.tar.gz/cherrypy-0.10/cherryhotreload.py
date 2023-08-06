#!/usr/bin/python

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

import sys, socket

if len(sys.argv)!=1 and len(sys.argv)!=2:
    print "Usage: CherryHotReload [port or socketFile]"
    sys.exit(-1)

if len(sys.argv)==1: portOrUnixFile="8000"
else: portOrUnixFile=sys.argv[1]

# Test if portOrUnixFile is AF_INET or AF_UNIX
# 2 possibilities for AF_INET: either "port" or "domain:port"
isAfInet=0
try:
    port=int(portOrUnixFile)
    domain="localhost"
    isAfInet=1
except: pass
if not isAfInet:
    try:
        domain,port=portOrUnixFile.split(':')
        port=int(port)
        isAfInet=1
    except: pass
        
if isAfInet:
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((domain, port))
else:
    s=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(portOrUnixFile)

s.send('HOTRELOAD NOW HTTP/1.1\r\n')
s.close()
print "Hot reload command sent"
