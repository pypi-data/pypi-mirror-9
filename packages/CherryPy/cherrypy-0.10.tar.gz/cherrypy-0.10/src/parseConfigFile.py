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

##################################
# Parse configuration file to get deployment option
##################################

# Default values for all parameters

global _logToScreen, _logFile, _socketHost, _socketPort, _socketFile, _protocolVersion, _reverseDNS, _socketQueueSize
global _processPool, _threading, _forking, _threadPool, _sslKeyFile, _sslCertificateFile
global _typeOfRequests, _staticContentList, _flushCacheDelay, _sessionStorageType
global _sessionTimeout, _sessionCookieName, _sessionStorageFileDir, _sessionCleanUpDelay
global _sslClientCertificateVerification, _sslCACertificateFile, _sslVerifyDepth

_logToScreen=1 # Should logs be output to screen or not
_logFile="" # Default log file

# Parameters used to tell which socket the server should listen on
# Note that socketPort and socketFile conflict wich each other: if one has a non-null value, the other one should be null
_socketHost=''
_socketPort=0
_socketFile='' # Used if server should listen on AF_UNIX socket
_reverseDNS=0
_socketQueueSize=5 # Size of the socket queue
_protocolVersion="HTTP/1.0"

# Parameters used to tell what kind of server we want
# Note that numberOfProcesses, threading and forking conflict wich each other: if one has a non-null value, the other ones should be null (for numberOfProcesses, null means equal to one)
_processPool=1 # Used if we want to fork n processes at the beginning. In this case, all processes will listen on the same socket (this only works on unix)
_threading=0 # Used if we want to create a new thread for each request
_forking=0 # Used if we want to create a new process for each request
_threadPool=1 # Used if we want to create a pool of threads at the beginning

# Variables used to tell if this is an SSL server
_sslKeyFile=""
_sslCertificateFile=""

_sslClientCertificateVerification=0
_sslCACertificateFile=""
_sslVerifyDepth=1

# Variable used to determine what types of request to accept
_typeOfRequests=('web', )

# Variable used to serve static content
_staticContentList=[]

# Variable used to flush cache
_flushCacheDelay=0

# Variable used for session handling
_sessionStorageType=""
_sessionTimeout=60 # In minutes
_sessionCleanUpDelay=60 # In minutes
_sessionCookieName="CherryPySession"
_sessionStorageFileDir=""

# Read parameters from configFile
try: _logToScreen=int(configFile.get('server', 'logToScreen'))
except: pass
try: _logFile=configFile.get('server', 'logFile')
except: pass
try: _socketHost=configFile.get('server', 'socketHost')
except: pass
try: _protocolVersion=configFile.get('server', 'protocolVersion')
except: pass
try: _socketPort=int(configFile.get('server', 'socketPort'))
except:pass
try: _socketFile=configFile.get('server', 'socketFile')
except: pass
try: _reverseDNS=int(configFile.get('server', 'reverseDNS'))
except: pass
try: _socketQueueSize=int(configFile.get('server', 'socketQueueSize'))
except: pass
try: _processPool=int(configFile.get('server', 'processPool'))
except: pass
try: _threadPool=int(configFile.get('server', 'threadPool'))
except: pass
try: _threading=int(configFile.get('server', 'threading'))
except: pass
try: _forking=int(configFile.get('server', 'forking'))
except: pass
try: _sslKeyFile=configFile.get('server', 'sslKeyFile')
except: pass
try: _sslCertificateFile=configFile.get('server', 'sslCertificateFile')
except: pass
try: _sslClientCertificateVerification=int(configFile.get('server', 'sslClientCertificateVerification'))
except: pass
try: _sslCACertificateFile=configFile.get('server', 'sslCACertificateFile')
except: pass
try: _sslVerifyDepth=int(configFile.get('server', 'sslVerifyDepth'))
except: pass
try: _typeOfRequests=configFile.get('server', 'typeOfRequests').split(',')
except: pass
try: _sessionStorageType=configFile.get('session', 'storageType')
except: pass
try: _sessionTimeout=float(configFile.get('session', 'timeout'))
except: pass
try: _sessionCleanUpDelay=float(configFile.get('session', 'cleanUpDelay'))
except: pass
try: _sessionCookieName=configFile.get('session', 'cookieName')
except: pass
try: _sessionStorageFileDir=configFile.get('session', 'storageFileDir')
except: pass
try:
    staticDirList=configFile.options('staticContent')
    for staticDir in staticDirList:
        staticDirTarget=configFile.get('staticContent', staticDir)
        _staticContentList.append((staticDir, staticDirTarget))
except: pass
try: _flushCacheDelay=float(configFile.get('cache', 'flushCacheDelay'))
except: pass

# Output parameters so that user can visually check values
logMessage("Reading parameters from %s ..."%configFileName)
logMessage("Server parameters:")
logMessage("  logToScreen: %s"%_logToScreen)
logMessage("  logFile: %s"%_logFile)
logMessage("  protocolVersion: %s"%_protocolVersion)
logMessage("  socketHost: %s"%_socketHost)
logMessage("  socketPort: %s"%_socketPort)
logMessage("  socketFile: %s"%_socketFile)
logMessage("  reverseDNS: %s"%_reverseDNS)
logMessage("  socketQueueSize: %s"%_socketQueueSize)
if _processPool!=1: _processPoolStr=_processPool
else: _processPoolStr='0'
logMessage("  processPool: %s"%_processPoolStr)
if _threadPool!=1: _threadPoolStr=_threadPool
else: _threadPoolStr='0'
logMessage("  threadPool: %s"%_threadPoolStr)
logMessage("  threading: %s"%_threading)
logMessage("  forking: %s"%_forking)
logMessage("  sslKeyFile: %s"%_sslKeyFile)
if _sslKeyFile:
    logMessage("  sslCertificateFile: %s"%_sslCertificateFile)
    logMessage("  sslClientCertificateVerification: %s"%_sslClientCertificateVerification)
    logMessage("  sslCACertificateFile: %s"%_sslCACertificateFile)
    logMessage("  sslVerifyDepth: %s"%_sslVerifyDepth)
    logMessage("  typeOfRequests: %s"%str(_typeOfRequests))
    logMessage("  flushCacheDelay: %s min"%_flushCacheDelay)
logMessage("  sessionStorageType: %s"%_sessionStorageType)
if _sessionStorageType:
    logMessage("  sessionTimeout: %s min"%_sessionTimeout)
    logMessage("  cleanUpDelay: %s min"%_sessionCleanUpDelay)
    logMessage("  sessionCookieName: %s"%_sessionCookieName)
    logMessage("  sessionStorageFileDir: %s"%_sessionStorageFileDir)
logMessage("  staticContent: %s"%_staticContentList)

# Check that parameters are correct and that they don't conflict with each other
if _protocolVersion not in ("HTTP/1.1", "HTTP/1.0"):
    raise "CherryError: protocolVersion must be 'HTTP/1.1' or 'HTTP/1.0'"
if _reverseDNS not in (0,1): raise "CherryError: reverseDNS must be '0' or '1'"
if _socketFile and not hasattr(socket, 'AF_UNIX'): raise "CherryError: Configuration file has socketFile, but this is only available on Unix machines"
if _processPool!=1 and not hasattr(os, 'fork'): raise "CherryError: Configuration file has processPool, but forking is not available on this operating system"
if _forking and not hasattr(os, 'fork'): raise "CherryError: Configuration file has forking, but forking is not available on this operating system"
if _sslKeyFile:
    try:
        global SSL
        from OpenSSL import SSL
    except: raise "CherryError: PyOpenSSL 0.5.1 or later must be installed to use SSL. You can get it from http://pyopenssl.sourceforge.net"
if 'xmlRpc' in _typeOfRequests:
    try:
        global xmlrpclib
        import xmlrpclib
    except: raise "CherryError: xmlrpclib must be installed to use XML-RPC. It is included in Python-2.2 and higher, or else you can get it from http://www.pythonware.com"
if _socketPort and _socketFile: raise "CherryError: In configuration file: socketPort and socketFile conflict with each other"
if not _socketFile and not _socketPort: _socketPort=8000 # Default port
if _processPool==1: severalProcs=0
else: severalProcs=1
if _threadPool==1: severalThreads=0
else: severalThreads=1
if severalThreads+severalProcs+_threading+_forking>1: raise "CherryError: In configuration file: threadPool, processPool, threading and forking conflict with each other"
if _sslKeyFile and not _sslCertificateFile: raise "CherryError: Configuration file has sslKeyFile but no sslCertificateFile"
if _sslCertificateFile and not _sslKeyFile: raise "CherryError: Configuration file has sslCertificateFile but no sslKeyFile"
try: sys.stdout.flush()
except: pass

for typeOfRequest in _typeOfRequests:
    if typeOfRequest not in ('xmlRpc', 'web'): raise "CherryError: Configuration file an invalid typeOfRequest: '%s'"%typeOfRequest

if _sessionStorageType not in ('', 'custom', 'ram', 'file', 'cookie'): raise "CherryError: Configuration file an invalid sessionStorageType: '%s'"%_sessionStorageType
if _sessionStorageType in ('custom', 'ram', 'cookie') and _sessionStorageFileDir!='': raise "CherryError: Configuration file has sessionStorageType set to 'custom, 'ram' or 'cookie' but a sessionStorageFileDir is specified"
if _sessionStorageType=='file' and _sessionStorageFileDir=='': raise "CherryError: Configuration file has sessionStorageType set to 'file' but no sessionStorageFileDir"
if _sessionStorageType=='ram' and (_forking or severalProcs):
    print "CherryWarning: 'ram' sessions might be buggy when using several processes"

