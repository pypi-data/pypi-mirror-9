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

# Server that handles thread pooling by Kevin Manley

import SocketServer
import socket
import threading
import Queue
import sys
import threading

_SHUTDOWNREQUEST = (0,0)

class ServerThread(threading.Thread):
    def __init__(self, RequestHandlerClass, requestQueue, threadIndex):
        threading.Thread.__init__(self)
        self._RequestHandlerClass = RequestHandlerClass
        self._requestQueue = requestQueue
        self._threadIndex = threadIndex
        self.setName("RUNNING")
        
    def run(self):
        initThread(self._threadIndex)
        #print "ServerThread %s running..." % threading.currentThread()
        while 1:
            request, client_address = self._requestQueue.get()
            if (request, client_address) == _SHUTDOWNREQUEST:
                #print "ServerThread %s got SHUTDOWN token" % threading.currentThread()
                return
            # print "ServerThread %s got request from %s" % (threading.currentThread(), client_address )
            if self.verify_request(request, client_address):            
                try:
                    self.process_request(request, client_address)
                except:
                    self.handle_error(request, client_address)
                    self.close_request(request)
            else:
                self.close_request(request)

    def verify_request(self, request, client_address):
        """Verify the request.  May be overridden.
        Return 1 if we should proceed with this request."""
        return 1

    def process_request(self, request, client_address):
        self._RequestHandlerClass(request, client_address, self)        
        self.close_request(request)

    def close_request(self, request):
        """Called to clean up an individual request."""
        request.close()

    def handle_error(self, request, client_address):
        """Handle an error gracefully.  May be overridden.
        The default is to print a traceback and continue.
        """
        import traceback, StringIO
        bodyFile=StringIO.StringIO()
        traceback.print_exc(file=bodyFile)
        errorBody=bodyFile.getvalue()
        bodyFile.close()
        logMessage(errorBody)
        

class PooledThreadServer(SocketServer.TCPServer):

    allow_reuse_address = 1

    """A TCP Server using a pool of worker threads. This is superior to the
       alternatives provided by the Python standard library, which only offer
       (1) handling a single request at a time, (2) handling each request in
       a separate thread (via ThreadingMixIn), or (3) handling each request in
       a separate process (via ForkingMixIn). It's also superior in some ways
       to the pure async approach used by Twisted because it allows a more
       straightforward and simple programming model in the face of blocking
       requests (i.e. you don't have to bother with Deferreds).""" 
    def __init__(self, serverAddress, numThreads, RequestHandlerClass, ThreadClass=ServerThread):
        assert(numThreads > 0)

        # I know it says "do not override", but I have to in order to implement SSL support !
        SocketServer.BaseServer.__init__(self, serverAddress, RequestHandlerClass)
        if _sslKeyFile:
            self.socket=SSL.Connection(_sslCtx, socket.socket(self.address_family, self.socket_type))
        else:
            self.socket=socket.socket(self.address_family, self.socket_type)
        self.server_bind()
        self.server_activate()
        initAfterBind()

        self._numThreads = numThreads        
        self._RequestHandlerClass = RequestHandlerClass
        self._ThreadClass = ThreadClass
        self._requestQueue = Queue.Queue()
        self._workerThreads = []

    def createThread(self, threadIndex):
        return self._ThreadClass(self._RequestHandlerClass, self._requestQueue, threadIndex)
            
    def start(self):
        if self._workerThreads != []:
            return
        for i in xrange(self._numThreads):
            self._workerThreads.append(self.createThread(i))        
        for worker in self._workerThreads:
            worker.start()
            
    def server_close(self):
        """Override server_close to shutdown thread pool"""
        #print "%s shutting down..." % str(self)
        SocketServer.TCPServer.server_close(self)
        for worker in self._workerThreads:
            self._requestQueue.put(_SHUTDOWNREQUEST)
        for worker in self._workerThreads:
            #print "waiting for %s to exit..." % str(worker)
            worker.join()
        self._workerThreads = []
        #print "%s was shutdown gracefully" % str(self)

    def server_activate(self):
        """Override server_activate to set timeout on our listener socket"""
        if hasattr(self.socket, 'settimeout'): self.socket.settimeout(2)
        elif hasattr(self.socket, 'set_timeout'): self.socket.set_timeout(2)
        SocketServer.TCPServer.server_activate(self)

    def server_bind(self):
        """Override server_bind to store the server name."""
        #SocketServer.TCPServer.server_bind(self)
        #host, port = self.socket.getsockname()
        #if _reverseDNS: self._serverName = socket.getfqdn(host)
        #else: self._serverName = host
        #self._serverPort = port
        #print "PooledThreadServer bound to %s:%s" % (self._serverName, self._serverPort)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind(self.server_address)

    def shutdown(self):
        """Gracefully shutdown a server that is serve_forever()ing."""
        self.__running = 0

    def shutdownCtrlC(self):
        self.server_close()

    def serve_forever(self):
        """Handle one request at a time until doomsday (or shutdown is called)."""
        if self._workerThreads == []:
            self.start()
        self.__running = 1
        while self.__running:
            if not self.handle_request():
                break
        self.server_close()            
        
    def handle_request(self):
        """Override handle_request to enqueue requests rather than handle
           them synchronously. Return 1 by default, 0 to shutdown the
           server."""
        try:
            if _debug:
                for t in threading.enumerate():
                    if t.getName()=="NOT RUNNING": return 0
            request, client_address = self.get_request()
            #if hasattr(request,'setblocking'): # Jython doesn't have setblocking
            #    request.setblocking(1)
        except _timeoutError:
            # The only reason for the timeout is so we can notice keyboard
            # interrupts on Win32, which don't interrupt accept() by default
            return 1
        except KeyboardInterrupt:
            print "<Ctrl-C> hit: shutting down"
            return 0
        except socket.error, e:
            return 1
        self._requestQueue.put((request, client_address))
        return 1

    def get_request(self):
        # With Python 2.3 it seems that an accept socket in timeout (nonblocking) mode
        #  results in request sockets that are also set in nonblocking mode. Since that doesn't play
        #  well with makefile() (where wfile and rfile are set in SocketServer.py) we explicitly set
        #  the request socket to blocking

        request, client_address = self.socket.accept()
        # logMessage("Accepted: %s" % repr(client_address), 9)
        if hasattr(request,'setblocking'): # Jython doesn't have setblocking
            request.setblocking(1)
        return request, client_address
