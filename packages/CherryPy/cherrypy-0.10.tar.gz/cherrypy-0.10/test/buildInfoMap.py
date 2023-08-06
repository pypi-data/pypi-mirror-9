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

import os, sys

def buildInfoMap(python2):
    print "Checking which python versions are installed..."
    for version, infoMap in python2.items():
        # Check if this version of python is installed:
        path=infoMap.get('path', "")
        if not path: path="python2.%s"%version
        exactVersion=os.popen('%s -c "import sys; print sys.version"'%path).read().strip()
        if exactVersion:
            exactVersionShort=exactVersion.split()[0]
            print "    Found version %s"%exactVersionShort
            python2[version]['exactVersion']=exactVersion
            python2[version]['exactVersionShort']=exactVersionShort
            python2[version]['path']=path
            if exactVersionShort.find("2.%s"%version)!=0:
                print
                print "*************************"
                print "Error: the path for python2.%s appears to run python%s"%(version, exactVersionShort)
                print 'By default, this script expects the python binaries to be in your PATH and to be called "python2.1", "python2.2", ...'
                print "If your setup is different, please edit this script and change the path for the python binary"
                sys.exit(-1)
        else:
            print "    Version 2.%s not found"%version
            del python2[version]

    if not python2:
        print
        print "*************************"
        print "Error: couldn't find any python distribution on your machine."
        print 'By default, this script expects the python binaries to be in your PATH and to be called "python2.1", "python2.2", ...'
        print "If your setup is different, please edit this script and change the path for the python binary"
        sys.exit(-1)
    print
    print "Finding out what modules are installed for these versions..."
    for version, infoMap in python2.items():
        print "    Checking modules for python%s..."%infoMap['exactVersionShort']

        # Test if python has fork
        res=os.popen('%s -c "import sys; sys.stderr=sys.stdout; import os; print hasattr(os,\'fork\')"'%infoMap['path']).read()
        if res.find('1')!=-1 or res.find('True')!=-1:
            print "        os.fork available"
            infoMap['hasFork']=1
        else:
            print "        os.fork not available"
            infoMap['hasFork']=0

        # Test if threads are available
        res=os.popen('%s -c "import sys; sys.stderr=sys.stdout; import thread"'%infoMap['path']).read()
        if res.find("ImportError")==-1:
            print "        thread available"
            infoMap['hasThread']=1
        else:
            print "        thread not available"
            infoMap['hasThread']=0

        # Test if pyOpenSSL is available
        res=os.popen('%s -c "import sys; sys.stderr=sys.stdout; from OpenSSL import SSL"'%infoMap['path']).read()
        if res.find("ImportError")==-1:
            print "        pyOpenSSL available"
            infoMap['hasPyOpenSSL']=1
        else:
            print "        pyOpenSSL not available"
            infoMap['hasPyOpenSSL']=0

        # Test if xmlrpclib is available
        res=os.popen('%s -c "import sys; sys.stderr=sys.stdout; import xmlrpclib"'%infoMap['path']).read()
        if res.find("ImportError")==-1:
            print "        xmlrpclib available"
            infoMap['hasXmlrpclib']=1
        else:
            print "        xmlrpclib not available"
            infoMap['hasXmlrpclib']=0

    return python2
