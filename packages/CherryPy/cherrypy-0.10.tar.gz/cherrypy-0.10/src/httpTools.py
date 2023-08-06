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
# Common Service Code for CherryPy
##################################
import mimetypes, sha
mimetypes.types_map['.dwg']='image/x-dwg'
mimetypes.types_map['.ico']='image/x-icon'

def _parseFirstLine(data):
    data = str(data) # Get rid of unicode
    request.path=data.split()[1]
    if request.path and request.path[0]=='/': request.path=request.path[1:] # Remove starting '/' if any
    request.path=request.path.replace('&amp;', '&') # This case happens for some reason ...
    request.browserUrl=request.path
    request.paramMap={}
    request.filenameMap={}
    request.fileTypeMap={}
    request.paramTuple=()
    request.isXmlRpc=0
    i=request.path.find('?')
    if i!=-1:
        if request.path[i+1:]:
            k=request.path[i+1:].find('?')
            if k!=-1:
                j=request.path[:k].rfind('=')
                if j!=-1: request.path=request.path[:j+1] + urllib.quote_plus(request.path[j+1:])
            for _paramStr in request.path[i+1:].split('&'):
                _sp=_paramStr.split('=')
                if len(_sp) > 2:
                    j=_paramStr.find('=')
                    _sp=(_paramStr[:j],_paramStr[j+1:])
                if len(_sp)==2:
                    _key, _value=_sp
                    _value=urllib.unquote_plus(_value)
                    if request.paramMap.has_key(_key):
                        # Already has a value: make a list out of it
                        if type(request.paramMap[_key])==type([]):
                            # Already is a list: append the new value to it
                            request.paramMap[_key].append(_value)
                        else:
                            # Only had one value so far: start a list
                            request.paramMap[_key]=[request.paramMap[_key], _value]
                    else:
                        request.paramMap[_key]=_value
        request.path=request.path[:i]

    if request.path and request.path[-1]=='/': request.path=request.path[:-1] # Remove trailing '/' if any
    
def _parsePostData(_rfile):
    # Read request body and put it in _data
    _len = int(request.headerMap.get("content-length","0"))
    if _len: _data=_rfile.read(_len)
    else: _data=""

    request.isXmlRpc=0
    # Try to parse request body as an XML-RPC call
    if 'xmlRpc' in _typeOfRequests and _data and request.headerMap.get("content-type","") == "text/xml":
        _xmlRpcPathList = []
        if request.path == 'RPC2': pass
        elif request.path.find('/') > -1: _xmlRpcPathList = request.path.split('/')
        elif not request.path: pass
        else: _xmlRpcPathList = [request.path]
        try:
            try: request.paramTuple,_thisXmlRpcMethod=xmlrpclib.loads(_data)
            except: raise "XML-RPC ERROR"
            _thisXmlRpcMethod = str(_thisXmlRpcMethod) # Get rid of unicode
            request.isXmlRpc=1 # If parsing worked, it is an XML-RPC request
            _xmlRpcPathList += _thisXmlRpcMethod.split('.')
        except "XML-RPC ERROR":
            # error reading data; must not have been an xmlrpc file
            pass

    if request.isXmlRpc:
        request.path = '/'.join(_xmlRpcPathList)
    else:
        # It's a normal browser call
        # Put _data in a StringIO so FieldStorage can read it
        _newRfile=cStringIO.StringIO(_data)
        _forms=cgi.FieldStorage(fp=_newRfile, headers=request.headerMap, environ={'REQUEST_METHOD':'POST'}, keep_blank_values=1)
        for _key in _forms.keys():
            # Check if it's a list or not
            _valueList=_forms[_key]
            if type(_valueList)==type([]):
                # It's a list of values
                request.paramMap[_key] = []
                request.filenameMap[_key] = []
                request.fileTypeMap[_key] = []
                for item in _valueList:
                    request.paramMap[_key].append(item.value)
                    request.filenameMap[_key].append(item.filename)
                    request.fileTypeMap[_key].append(item.type)
            else:
                # It's a single value
                # In case it's a file being uploaded, we save the filename in a map (user might need it)
                request.paramMap[_key]=_valueList.value
                request.filenameMap[_key]=_valueList.filename
                request.fileTypeMap[_key]=_valueList.type

def _insertIntoHeaderMap(key,value):
    request.headerMap[key.lower()]=value

def _doRequest(_wfile):
    try:
        _handleRequest(_wfile)
    except:
        _err=""
        _exc_info_1=sys.exc_info()[1]
        if hasattr(_exc_info_1,'args') and len(_exc_info_1.args)>=1:
            _err=_exc_info_1.args[0]
        if _err=='global name \'sessionMap\' is not defined':
            _error="CherryError:\n"
            _error+="    Session data is now manipulated through \"request.sessionMap\" instead of just \"sessionMap\".\n"
            _error+="    Check out the HowTo about sessions on the cherrypy.org website to learn how to use sessions.\n"
            _wfile.write('%s 200 OK\r\n' % _protocolVersion)
            _wfile.write('Content-Type: text/plain\r\n')
            _wfile.write('Content-Length: %s\r\n'%len(_error))
            _wfile.write('\r\n')
            _wfile.write(_error)
            return
        elif _err=="_emptyClass instance has no attribute 'sessionMap'":
            _error="CherryError:\n"
            _error+="    You are trying to use sessions but sessions are not enabled in the config file.\n"
            _error+="    Check out the HowTo about sessions on the cherrypy.org website to learn how to use sessions.\n"
            _wfile.write('%s 200 OK\r\n' % _protocolVersion)
            _wfile.write('Content-Type: text/plain\r\n')
            _wfile.write('Content-Length: %s\r\n'%len(_error))
            _wfile.write('\r\n')
            _wfile.write(_error)
            return

        try:
            onError()
            _wfile.write('%s %s\r\n' % (response.headerMap['protocolVersion'], response.headerMap['status']))
            if response.headerMap.has_key('content-length') and response.headerMap['content-length']==0:
                response.headerMap['content-length']=len(response.body)
            for _key, _valueList in response.headerMap.items():
                if _key not in ('status', 'protocolVersion'):
                    if type(_valueList)!=type([]): _valueList=[_valueList]
                    for _value in _valueList:
                        _wfile.write('%s: %s\r\n'%(_key, _value))
            _wfile.write('\r\n')
            _wfile.write(response.body)
        except:
            import traceback, StringIO
            _bodyFile=StringIO.StringIO()
            traceback.print_exc(file=_bodyFile)
            _body=_bodyFile.getvalue()
            _bodyFile.close()
            _wfile.write('%s 200 OK\r\n' % _protocolVersion)
            _wfile.write('Content-Type: text/plain\r\n')
            _wfile.write('Content-Length: %s\r\n'%len(_body))
            _wfile.write('\r\n')
            _wfile.write(_body)

def _sendResponse(_wfile):
    # Save page in the cache if needed
    _cacheKey=""
    try: _cacheKey=request.cacheKey # Cannot use "hasattr", because it fails under jython when threading is turned on
    except: pass
    if _cacheKey:
        _cacheMap[request.cacheKey]=(request.cacheExpire, response.headerMap, response.body)

    # Save session data
    if _sessionStorageType and not request.isStaticFile:
        _sessionId=response.simpleCookie[_sessionCookieName].value
        _expirationTime=time.time()+_sessionTimeout*60
        ramOrFileOrCookieOrCustomSaveSessionData(_sessionId, request.sessionMap, _expirationTime)

    _wfile.write('%s %s\r\n' % (response.headerMap['protocolVersion'], response.headerMap['status']))
    for _key, _valueList in response.headerMap.items():
        if _key not in ('status', 'protocolVersion'):
            if type(_valueList)!=type([]): _valueList=[_valueList]
            for _value in _valueList:
                _wfile.write('%s: %s\r\n'%(_key, _value))
    # Send response cookies
    _cookie=response.simpleCookie.output()
    # print "Sending back cookie:", _cookie
    if _cookie:
        _wfile.write(_cookie+'\r\n')
    _wfile.write('\r\n')
    _wfile.write(response.body)

def _sendCachedPageIfPossible(_now,_wfile):
    _cacheKey=""
    try: _cacheKey=request.cacheKey # Cannot use "hasattr", because it fails under jython when threading is turned on
    except: pass
    if _cacheKey:
        # Use caching for this page
        if _cacheMap.has_key(request.cacheKey) and _cacheMap[request.cacheKey][0]>=_now:
            # This page is already in the cache and it hasn't expired yet: use the cached version
            dummy, response.headerMap, response.body=_cacheMap[request.cacheKey]
            initResponse()
            request.cacheKey='' # No need to save the page in the cache again
            _sendResponse(_wfile)
            return 1
        # else:
        #     Either the page has never been cached, or the cached version expired
        #     In the case, we build the page normally and it will be saved in the cache
        #    in the _sendResponse function
    return 0

def _handleRequest(_wfile):
    _now = time.time()
    _year, _month, _day, _hh, _mm, _ss, _wd, _y, _z = time.gmtime(_now)
    _date="%s, %02d %3s %4d %02d:%02d:%02d GMT"%(_weekdayname[_wd],_day,_monthname[_month],_year,_hh,_mm,_ss)
    response.headerMap={"status": "200 OK", "protocolVersion": _protocolVersion, "content-type": "text/html", "server": "CherryPy/0.10", "date": _date, "set-cookie": [], "content-length": 0}

    # Two variables used for streaming
    response.wfile = _wfile
    response.sendResponse = 1

    if _sslKeyFile:
        request.base="https://"+request.headerMap['host']
    else:
        request.base="http://"+request.headerMap['host']
    request.browserUrl=request.base+'/'+request.browserUrl
    request.isStaticFile = 0

    # Flush the cache if needed:
    global _lastCacheFlushTime
    if _flushCacheDelay and _cacheMap and _lastCacheFlushTime+_flushCacheDelay*60<=_now:
        _lastCacheFlushTime=_now
        for key, (expire, dummy, dummy) in _cacheMap.items():
            if expire<=_now:
                del _cacheMap[key]

    # Clean up expired sessions if needed:
    global _lastSessionCleanUpTime
    if _sessionStorageType and _sessionCleanUpDelay and _lastSessionCleanUpTime+_sessionCleanUpDelay*60<=_now:
        _lastSessionCleanUpTime=_now
        ramOrFileOrCookieOrCustomCleanUpOldSessions()

    # Perform some initial operations (such as rewriting url ...)
    request.originalPath=request.path
    request.originalParamMap=request.paramMap
    request.originalParamTuple=request.paramTuple

    initRequest()

    _path=request.path

    # Handle static directories
    for urlDir, fsDir in _staticContentList:
        if _path == urlDir or _path[:len(urlDir)+1]==urlDir+'/':

            request.isStaticFile = 1

            if _sendCachedPageIfPossible(_now, _wfile): return

            _fname = fsDir+_path[len(urlDir):] 
            _stat = os.stat(_fname)
            if type(_stat) == type(()): # Python2.1
                _modifTime = _stat[9]
            else:
                _modifTime = _stat.st_mtime
                
            _strModifTime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(_modifTime))

            # Check if browser sent "if-modified-since" in request header
            if request.headerMap.has_key('if-modified-since'):
                # Check if if-modified-since date is the same as _strModifTime
                if request.headerMap['if-modified-since'] == _strModifTime:
                    response.headerMap = {'status': 304, 'protocolVersion': _protocolVersion, 'date': _date}
                    response.body = ''
                    initResponse()
                    _sendResponse(_wfile)
                    return

            response.headerMap['last-modified'] = _strModifTime
            _f=open(_fname, 'rb')
            response.body=_f.read()
            response.headerMap['content-length']=len(response.body)
            _f.close()
            # Set content-type based on filename extension
            _i=_path.rfind('.')
            if _i!=-1: _ext=_path[_i:]
            else: _ext=""
            _contentType=mimetypes.types_map.get(_ext, "text/plain")
            response.headerMap['content-type']=_contentType
            initResponse()
            _sendResponse(_wfile)
            return

    # Get session data
    if _sessionStorageType and not request.isStaticFile:
        _now=time.time()
        # First, get sessionId from cookie
        try: _sessionId=request.simpleCookie[_sessionCookieName].value
        except: _sessionId=None
        if _sessionId:
            # Load session data from wherever it was stored
            _sessionData = ramOrFileOrCookieOrCustomLoadSessionData(_sessionId)
            if _sessionData == None:
                _sessionId = None
            else:
                request.sessionMap, _expirationTime = _sessionData
                # Check that is hasn't expired
                if _now > _expirationTime:
                    # Session expired
                    _sessionId = None

        # Create a new sessionId if needed
        if not _sessionId:
            request.sessionMap={}
            _sessionId=_generateSessionId()
            request.sessionMap['_sessionId'] = _sessionId

        response.simpleCookie[_sessionCookieName]=_sessionId
        response.simpleCookie[_sessionCookieName]['path']='/'
        response.simpleCookie[_sessionCookieName]['version']=1

    initNonStaticRequest()

    if _sendCachedPageIfPossible(_now, _wfile): return

    _path=request.path
    # Special case when url is just the host name
    if not _path: _path='index'

    # Work on path:
    # a/b/c/d -> a_b_c.d()
    # c -> root.c()

    #if request.isXmlRpc: _pathList=_path.split('.')
    #else:
    _pathList=_path.split('/')
    #print "_path:", _path
    if len(_pathList)==1: _pathList=['root']+_pathList
    _function=None
    _myClass='_'.join(_pathList)
    if _myClass[:5] == 'root_': _myClass = _myClass[5:]
    _myClass2='_'.join(_pathList[:-1])
    _function=_pathList[-1]
    _originalFunction = _function
    # If both mask/view and class have same name, make the mask/view default.
    if maskAndViewMap.has_key(_myClass2) and maskAndViewMap[_myClass2].has_key(_function): _myClass = _myClass2
    # If the path leads to a class, call index by default.
    elif maskAndViewMap.has_key(_myClass): _function = 'index'

    _myClass=str(_myClass) # For some reason, _myClass was sometimes unicode (when using XML-RPC)
    # print "_myClass:", `_myClass`, "__function:", _function

    # Check that class/method exist
    try: maskAndViewMap[_myClass][_function]
    except KeyError:
        tried = 'tried "%s.%s"' % (_myClass2, _originalFunction)
        if request.path != "":
            tried +=  ' and "%s.index"' % _myClass
        raise str("CherryError: couldn't map URL to an existing non-hidden mask or view (%s)" % tried)
    #if not maskAndViewMap.has_key(_myClass): raise str('CherryError: CherryClass "%s" doesn\'t exist'%_myClass)
    #elif not maskAndViewMap[_myClass].has_key(_function): raise str('CherryError: CherryClass "%s" doesn\'t have any view or mask method called "%s"'%(_myClass, _function))

    # Check that it is not a browser call to an XML-RPC method:
    if xmlrpcMaskAndViewMap and not request.isXmlRpc and xmlrpcMaskAndViewMap.has_key(_myClass) and xmlrpcMaskAndViewMap[_myClass].has_key(_function):
        raise str('CherryError: Method "%s" of CherryClass "%s" is an XML-RPC method'%(_function, _myClass))

    # Check that it is not an XML-RPC call to a regular metohd:
    if request.isXmlRpc and (not xmlrpcMaskAndViewMap.has_key(_myClass) or not xmlrpcMaskAndViewMap[_myClass].has_key(_function)):
        raise str('CherryError: method "%s" of CherryClass "%s" is not an xmlrpc method'%(_function, _myClass))

    # Get result by calling class method
    _theObj=globals()[_myClass]
    _theMethod=getattr(_theObj,_function)
    if request.isXmlRpc:
        response.body=_theMethod(*(request.paramTuple))
    else:
        response.body=_theMethod(**(request.paramMap))

    initResponse()
    initNonStaticResponse()

    if request.isXmlRpc:
        # Marshall the result if it's an XML-RPC call
        # Wrap the response into a singleton tuple
        response.body=(response.body,)
        response.body=xmlrpclib.dumps(response.body, methodresponse=1)
        # Response type is text/xml for an XML-RPC call
        response.headerMap["content-type"]="text/xml"

    # Check response.body and set content-length if needed
    if type(response.body) != type(""):
        if type(response.body) == type(u""): # Potential gotcha: on jython, type("") == type(u"") !!
            raise "CherryError: The mask or view returned a unicode string instead of a regular string !"
        else:
            raise "CherryError: The mask or view didn't return a string !"
    if response.headerMap.has_key('content-length') and response.headerMap['content-length']==0:
        response.headerMap['content-length']=len(response.body)

    if response.sendResponse: _sendResponse(_wfile)

def _generateSessionId():
    s=''
    for i in range(50):
        s+=whrandom.choice(string.letters+string.digits)
    s+='%s'%time.time()
    return sha.sha(s).hexdigest()

