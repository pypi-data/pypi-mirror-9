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

"""CherryPy HTTP Server.

This module builds on BaseHTTPServer in a fashion similar to SimpleHTTPServer 
by implementing the standard GET and HEAD requests in a fairly straightforward manner.

"""

# python2.3 has settimeout by default, but previous version can use the "timeousocket" module
try:
    import timeoutsocket
    _timeoutError = timeoutsocket.Timeout
except:
    _timeoutError = ''

__all__ = ["CherryHTTPRequestHandler"]

import BaseHTTPServer, mimetypes, Cookie, whrandom, os.path, cPickle


class CherryHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """CherryPy HTTP request handler with the following commands:

        o  GET
        o  HEAD
        o  POST
        o  HOTRELOAD

    """

    def address_string(self):
        """ Try to do a reverse DNS based on [server]reverseDNS in the config file """
        if _reverseDNS: return BaseHTTPServer.BaseHTTPRequestHandler.address_string(self)
        else: return self.client_address[0]

    def cook_headers(self):
        """Process the headers in self.headers into the request.headerMap"""
        request.headerMap={}
        request.simpleCookie=Cookie.SimpleCookie()
        response.simpleCookie=Cookie.SimpleCookie()

        # Build headerMap
        for item in self.headers.items():
            # Warning: if there is more than one header entry for cookies (AFAIK, only Konqueror does that)
            # only the last one will remain in headerMap (but they will be correctly stored in request.simpleCookie)
            _insertIntoHeaderMap(item[0],item[1])

        # Handle cookies differently because on Konqueror, multiple cookies come on different lines with the same key
        cookieList = self.headers.getallmatchingheaders('cookie')
        for cookie in cookieList:
            request.simpleCookie.load(cookie)

        if not request.headerMap.has_key('remote-addr'):
            try:
                request.headerMap['remote-addr']=self.client_address[0]
                request.headerMap['remote-host']=self.address_string()
            except: pass

        # Set peer_certificate (in SSL mode) so the web app can examinate the client certificate
        try: request.peerCertificate = self.request.get_peer_certificate()
        except: pass

        logMessage("[%s] %s - %s"%((time.strftime("%Y/%m/%d %H:%M:%S")), request.headerMap.get('remote-addr', ''), self.raw_requestline[:-2]))

    def do_GET(self):
        """Serve a GET request."""
        request.method = 'GET'
        _parseFirstLine(self.raw_requestline)
        self.cook_headers()
        _doRequest(self.wfile)

    def do_HEAD(self): # Head is not implemented
        """Serve a HEAD request."""
        request.method = 'HEAD'
        _parseFirstLine(self.raw_requestline)
        self.cook_headers()
        _doRequest(self.wfile)

    def do_POST(self):
        """Serve a POST request."""
        request.method = 'POST'
        _parseFirstLine(self.raw_requestline)
        self.cook_headers()
        _parseIt = 1
        request.parsePostData = 1
        initRequestBeforeParse()
        if request.parsePostData: _parsePostData(self.rfile)
        request.rfile = self.rfile
        _doRequest(self.wfile)

    def do_HOTRELOAD(self):
        """Serve a HOTRELOAD request."""
        if _debug:
            logMessage("Starting hot reload ...")
            sys.stdout.flush()
            global hotReload
            hotReload=1
            try: execfile(_outputFile)
            except SystemExit, e: pass
        else:
            logMessage("Hot reload disabled when not in debug mode ...")

    if sys.platform[:4]!="java":
         # Don't use this for jython
         def setup(self):
             """ We have to override this to handle SSL (socket object from the OpenSSL package don't have the makefile method) """
             self.connection=self.request
             #self.rfile=self.connection.makefile('rb', self.rbufsize)
             #self.wfile=self.connection.makefile('wb', self.wbufsize)
             self.rfile=CherryFileObject(self.connection, 'rb', self.rbufsize)
             self.wfile=CherryFileObject(self.connection, 'wb', self.wbufsize)

    def log_message(self, format, *args):
        """ We have to override this to use our own logging mechanism """
        logMessage("%s - - [%s] %s\n" %
                         (self.address_string(),
                            self.log_date_time_string(),
                            format%args))

# I'm a bit confused here: "some" sockets have a "sendall" method, some don't.
# From my testing, the following sockets do have a "sendall" method:
#    - Regular sockets in Python2.2 or higher
#    - SSL sockets in pyOpenSSL-0.5.1 on Linux
# The following sockets don't have a "sendall" method
#    - Regular sockets in Python2.1 or lower
#    - SSL sockets in pyOpenSSL-0.5.1 on Windows (doh)
# So I'm just taking advantage of the sendall method when it's there. Otherwise, I'm using the good old way of doing it with "send" (but I'm afraid this might be blocking in some cases)

if sys.platform[:4]!="java":
    # Don't use this for jython
    class CherryFileObject(socket._fileobject):
        def flush(self):
            if self._wbuf:
                if hasattr(self._sock, "sendall"):
                    if type(self._wbuf)==type([]): # python2.3
                        self._sock.sendall("".join(self._wbuf))
                        self._wbuf=[]
                    else:
                        self._sock.sendall(self._wbuf)
                        self._wbuf=""
                else:
                    while self._wbuf:
                        _sentChar=self._sock.send(self._wbuf)
                        self._wbuf=self._wbuf[_sentChar:]
        def __del__(self):
            try: self.close()
            except: pass

class CherryThreadingMixIn(SocketServer.ThreadingMixIn):
    def process_request_thread(self, request, client_address):
        """Same as in BaseServer but as a thread.
        In addition, exception handling is done here.
        """
        try:
            self.finish_request(request, client_address)
            self.close_request(request)
        except:
            self.handle_error(request, client_address)
            self.close_request(request)

    def process_request(self, request, client_address):
        """Start a new thread to process the request."""
        if _debug:
            for t in threading.enumerate():
                if t.getName() == "NOT RUNNING":
                    os._exit(-1)
        t = threading.Thread(target = self.process_request_thread, args = (request, client_address))
        if _debug: t.setName("RUNNING")
        t.start()

class CherryHTTPServer(BaseHTTPServer.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        # I know it says "do not override", but I have to in order to implement SSL support !
        SocketServer.BaseServer.__init__(self, server_address, RequestHandlerClass)
        if _sslKeyFile:
            self.socket=SSL.Connection(_sslCtx, socket.socket(self.address_family, self.socket_type))
        else:
            self.socket=socket.socket(self.address_family, self.socket_type)
        self.server_bind()
        self.server_activate()
        initAfterBind()

    def server_activate(self):
        """Override server_activate to set timeout on our listener socket"""
        if hasattr(self.socket, 'settimeout'): self.socket.settimeout(2)
        elif hasattr(self.socket, 'set_timeout'): self.socket.set_timeout(2)
        BaseHTTPServer.HTTPServer.server_activate(self)

    def server_bind(self):
        # Removed getfqdn call because it was timing out on localhost when calling gethostbyaddr
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def get_request(self):
        # With Python 2.3 it seems that an accept socket in timeout (nonblocking) mode
        #  results in request sockets that are also set in nonblocking mode. Since that doesn't play
        #  well with makefile() (where wfile and rfile are set in SocketServer.py) we explicitly set
        #  the request socket to blocking

        request, client_address = self.socket.accept()
        if hasattr(request,'setblocking'): # Jython doesn't have setblocking
            request.setblocking(1)
        return request, client_address

    def handle_request(self):
        """Override handle_request to trap timeout exception."""
        try:
            BaseHTTPServer.HTTPServer.handle_request(self)
        except _timeoutError:
            # The only reason for the timeout is so we can notice keyboard
            # interrupts on Win32, which don't interrupt accept() by default
            return 1
        except KeyboardInterrupt:
            print "<Ctrl-C> hit: shutting down"
            sys.exit(0)

    def shutdownCtrlC(self):
        self.shutdown()

def run_server(HandlerClass, ServerClass, server_address, _socketFile):
    """Run the HTTP request handler class."""
    global __myCherryHTTPServer
    if _socketFile:
        try: os.unlink(_socketFile) # So we can reuse the socket
        except: pass
        server_address=_socketFile
    if _threadPool>1:
        __myCherryHTTPServer = ServerClass(server_address, _threadPool, HandlerClass)
    else:
        __myCherryHTTPServer = ServerClass(server_address, HandlerClass)
    if _socketFile:
        try: os.chmod(_socketFile, 0777) # So everyone can access the socket
        except: pass

    if _sslKeyFile: servingWhat="HTTPS"
    else: servingWhat="HTTP"
    if _socketPort: onWhat="socket: ('%s', %s)" % (_socketHost, _socketPort)
    else: onWhat="socket file: %s"%_socketFile
    logMessage("Serving %s on %s"%(servingWhat, onWhat))

    # If _processPool is more than one, create new processes
    if _processPool>1:
        for i in range(_processPool):
            logMessage("Forking a kid")
            if not os.fork():
                # Kid
                initProcess(i)
                try: __myCherryHTTPServer.serve_forever()
                except KeyboardInterrupt:
                    print "<Ctrl-C> hit: shutting down"
                    __myCherryHTTPServer.shutdownCtrlC()
    else:
        try: __myCherryHTTPServer.serve_forever()
        except KeyboardInterrupt:
            print "<Ctrl-C> hit: shutting down"
            __myCherryHTTPServer.shutdownCtrlC()

def run(argv):
    mainInit(argv)
    if not globals().has_key('hotReload'):
        # If SSL is used, perform some initialization
        if _sslKeyFile:
            # Setup SSL mode
            global _sslCtx
            _sslCtx=SSL.Context(SSL.SSLv23_METHOD)
            # _sslCtx.set_options(SSL.OP_NO_SSLv2) # Doesn't work on Windows
            _sslCtx.use_privatekey_file(_sslKeyFile)
            _sslCtx.use_certificate_file(_sslCertificateFile)
            if _sslClientCertificateVerification:
                _sslCtx.set_verify_depth(_sslVerifyDepth)
                _sslCtx.load_verify_locations(_sslCACertificateFile)
                _sslCtx.set_timeout(5)
                def _sslContextCallback(conn, x509, error_num, error_depth, return_val):
                    if error_num == 0: return 1
                    else: return 0
                _sslCtx.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, _sslContextCallback)
        
        # If sessions are stored in files and we use threading, we need a lock on the file
        if (_threadPool>1 or _threading) and _sessionStorageType == 'file':
            global _sessionFileLock
            import threading
            _sessionFileLock = threading.RLock()
        
        import SocketServer
        if _socketFile:
            # AF_UNIX socket
            if _forking:
                class MyCherryHTTPServer(SocketServer.ForkingMixIn,CherryHTTPServer): address_family=socket.AF_UNIX
            elif _threading:
                import threading
                class MyCherryHTTPServer(CherryThreadingMixIn,CherryHTTPServer): address_family=socket.AF_UNIX
            else:
                class MyCherryHTTPServer(CherryHTTPServer): address_family=socket.AF_UNIX
        else:
            # AF_INET socket
            if _forking:
                class MyCherryHTTPServer(SocketServer.ForkingMixIn,CherryHTTPServer): pass
            elif _threading:
                class MyCherryHTTPServer(CherryThreadingMixIn,CherryHTTPServer):pass
            elif _threadPool>1:
                MyCherryHTTPServer=PooledThreadServer
            else:
                MyCherryHTTPServer=CherryHTTPServer
    
        MyCherryHTTPServer.request_queue_size = _socketQueueSize

        # Set protocol_version
        CherryHTTPRequestHandler.protocol_version = _protocolVersion

        run_server(CherryHTTPRequestHandler, MyCherryHTTPServer, (_socketHost, _socketPort), _socketFile)

def shutdown():
    __myCherryHTTPServer.shutdown()


