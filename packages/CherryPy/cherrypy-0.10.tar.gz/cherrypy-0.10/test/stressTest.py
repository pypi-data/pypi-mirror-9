import time
import threading
import socket


import sys, getopt
# usage "test.py threads requestsPerThread host page"

threadCount, requestsPerThread, host, page = sys.argv[1:]

origHost = host
if host.find(':') != -1: host, port = host.split(':')
else: port = 80

def grab_page():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    t0 = time.time()
    s.connect((host, int(port)))
    d = time.time() - t0
    if d > 10: print "more than 10ms"

    s.send('GET %s HTTP/1.0\r\n' % page)
    s.send('Host: %s\r\n' % origHost)
    s.send('\r\n')

    r = s.makefile('rb')
    data = r.read()
    r.close()
    if data.find('200 OK') == -1: print "Error, data:", repr(data)
 
class PageGrabber(threading.Thread):
    def run(self):
        for i in range(int(requestsPerThread)):
            grab_page()

tStart = time.time()

print "Starting..."

# Create the threads
threads = []
for i in range(int(threadCount)):
 t = PageGrabber()
 threads.append(t)
 t.start()

# Wait for all the threads to complete
for t in threads:
 t.join()

tEnd = time.time()
print "%.2f Time total program" % (tEnd - tStart)

