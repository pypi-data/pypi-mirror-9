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

import os, sys, socket

try:
    socketFile='put your socket file here'


    # Read data if any (in case of a POST)
    data=""
    if os.environ.has_key('CONTENT_LENGTH'):
        l=int(os.environ['CONTENT_LENGTH'])
        data=sys.stdin.read(l)

    s=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(socketFile)
    s.send('%s %s HTTP/1.1\r\n'%(os.environ['REQUEST_METHOD'], os.environ['REQUEST_URI']))
    s.send('Accept: text/html\r\n')
    s.send('Accept: text/plain\r\n')
    s.send('Accept: text/css\r\n')
    s.send('Accept: image/gif\r\n')
    s.send('Accept: image/jpeg\r\n')
    s.send('Host: %s\r\n'%os.environ['HTTP_HOST'])
    if os.environ.has_key('HTTP_USER_AGENT'):
        s.send('User-Agent: %s\r\n'%os.environ['HTTP_USER_AGENT'])
    if os.environ.has_key('HTTP_CGI_AUTHORIZATION'):
        s.send('Authorization: %s\r\n'%os.environ['HTTP_CGI_AUTHORIZATION'])
    if os.environ.has_key('CONTENT_LENGTH'):
        s.send('Content-Length: %s\r\n'%os.environ['CONTENT_LENGTH'])
    if os.environ.has_key('CONTENT_TYPE'):
        s.send('Content-Type: %s\r\n'%os.environ['CONTENT_TYPE'])
    if os.environ.has_key('HTTP_COOKIE'):
        s.send('Cookie: %s\r\n'%os.environ['HTTP_COOKIE'])
    if os.environ.has_key('USER_AGENT'):
        s.send('User-Agent: %s\r\n'%os.environ['USER_AGENT'])
    if os.environ.has_key('REMOTE_HOST'):
        s.send('Remote-Host: %s\r\n'%os.environ['REMOTE_HOST'])
    if os.environ.has_key('REMOTE_ADDR'):
        s.send('Remote-Addr: %s\r\n'%os.environ['REMOTE_ADDR'])
    if os.environ.has_key('HTTP_REFERER'):
        s.send('Referer: %s\r\n'%os.environ['HTTP_REFERER'])
    if os.environ.has_key('HTTP_ACCEPT_ENCODING'):
        s.send('Accept-Encoding: %s\r\n'%os.environ['HTTP_ACCEPT_ENCODING'])
    s.send('\r\n')
    if data: s.send(data)
    rfile=s.makefile('rb')
    firstLine=rfile.readline()
    status=firstLine.split()[1]
    data=rfile.read()
    rfile.close()

    # Remove "last-modified" header as it doesn't work well with Apache ...
    i = data.find('last-modified:')
    if i != -1:
        j = data.find('\r\n', i)
        data = data[:i] + data[j+2:]

    sys.stdout.write("Status: %s\r\n"%status)
    sys.stdout.write(data)

except:
    import os
    print "Content-type: text/plain"
    print
    print os.environ
    import traceback, StringIO
    bodyFile=StringIO.StringIO()
    traceback.print_exc(file=bodyFile)
    body=bodyFile.getvalue()
    bodyFile.close()
    print
    print "#################################"
    print "ERROR"
    print "#################################"
    print body
    print
    print "#################################"
    print "ENVIRON"
    print "#################################"
    print os.environ

