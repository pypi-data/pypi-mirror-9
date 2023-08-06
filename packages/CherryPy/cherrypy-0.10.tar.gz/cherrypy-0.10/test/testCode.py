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

import os,urllib,time,sys,signal,socket,httplib

def compileCode(infoMap, code, extraCompileOption):
    try: os.remove("Root.cpy")
    except OSError: pass
    try: os.remove("RootServer.py")
    except OSError: pass
    try: os.remove("RootServer.cfg")
    except OSError: pass

    # Check if we want to use -W something
    f=open("Root.cpy", "w")
    f.write(code)
    i = extraCompileOption.find("-W ") 
    if i != -1:
        j = extraCompileOption.find(' ', i + 3)
        if j == -1: j = len(extraCompileOption)
        whiteSpace = int(extraCompileOption[i+3:j])
    else: whiteSpace = 4

    f.write("""
CherryClass Shutdown:
view:
-INDENT-def dummy(self):
-INDENT--INDENT-return "OK"
-INDENT-def regular(self):
-INDENT--INDENT-os._exit(0)
-INDENT-def thread(self):
-INDENT--INDENT-for t in threading.enumerate(): t.setName("NOT RUNNING")
-INDENT--INDENT-return "OK"        
""".replace('-INDENT-', ' ' * whiteSpace))

    f.close()

    # Compile the file
    return os.popen("%s ../cherrypy.py --stderr2stdout -D %s Root.cpy"%(infoMap['path'], extraCompileOption)).read()

def getCompiledCode(testName, infoMap, code, extraCompileOption, failedList):
    res=compileCode(infoMap, code, extraCompileOption)
    if res.lower().find('error')!=-1:
        failedList.append(testName+" for python%s"%infoMap['exactVersionShort']+' failed: compilation failed (%s)'%res)
        print "*** FAILED ***"
        return
    f=open("RootServer.py", "rb")
    compiledCode=f.read()
    f.close()
    return compiledCode

def startServer(infoMap):
    # Start the server in another thread
    if not hasattr(os, "fork"): # win32 mostly
        pid=os.spawnl(os.P_NOWAIT, infoMap['path'], infoMap['path'], 'RootServer.py')
    else:
        pid=os.fork()
        if not pid:
            os.execlp(infoMap['path'],infoMap['path'],'RootServer.py')
    return pid

def getPage(url, cookies, isSSL=0, extraRequestHeader = []):
    data=""
    i=0
    response = None
    while i<10:
        try:
            if isSSL:
                conn=httplib.HTTPSConnection('127.0.0.1:8000')
            else:
                conn=httplib.HTTPConnection('127.0.0.1:8000')

            conn.putrequest("GET", "/"+url)

            conn.putheader("Host", "127.0.0.1")
            if cookies:
                cookieList = []
                for cookie in cookies:
                    i = cookie.find(' ')
                    j = cookie.find(';')
                    cookieList.append(cookie[i+1:j])
                cookieStr = '; '.join(cookieList)
                conn.putheader("Cookie", cookies[:j])

            for key, value in extraRequestHeader:
                conn.putheader(key, value)

            conn.endheaders()

            response=conn.getresponse()

            cookies=response.msg.getallmatchingheaders("Set-Cookie")

            data=response.read()

            conn.close()
            break
        except socket.error:
            time.sleep(0.5)
        i+=1
    return data, cookies, response

def getXmlrpc(url, func, isSSL=0):
    import xmlrpclib
    http="http"
    if isSSL: http+="s"
    if url: url='/'+url
    data=""
    i=0
    try:
        while i<10:
            try:
                testsvr=xmlrpclib.Server(http+"://127.0.0.1:8000"+url)
                data=eval("testsvr.%s"%func)
                break
            except socket.error:
                time.sleep(0.5)
            i+=1
    except xmlrpclib.Fault, msg:
        return msg
    return data


def shutdownServer(pid, mode, isSSL=0):
    if isSSL: h="https"
    else: h="http"
    if mode=='t':
        u=urllib.urlopen(h+"://127.0.0.1:8000/shutdown/thread")
        if hasattr(socket, 'sslerror'): sslError = socket.sslerror
        else: sslError = 'dummy'
        try: u=urllib.urlopen(h+"://127.0.0.1:8000/shutdown/dummy")
        except IOError: pass
        except sslError: pass
        except AttributeError: pass # Happens on Mac OS X when run with Python-2.3
    elif mode=='tp':
        try: sslError = socket.sslerror
        except: sslError = 'dummy'
        u=urllib.urlopen(h+"://127.0.0.1:8000/shutdown/thread")
        try: u=urllib.urlopen(h+"://127.0.0.1:8000/shutdown/dummy")
        except IOError: pass # Happens on Windows
        except sslError: pass # Happens on Windows for https requests
    else:
        try: u=urllib.urlopen(h+"://127.0.0.1:8000/shutdown/regular")
        except IOError: pass
        except AttributeError: pass # For Python2.3

def checkResult(testName, infoMap, serverMode, result, expectedResult, failedList, exactResult):
    if result==expectedResult or (exactResult==0 and result.find(expectedResult)!=-1): return 1
    else:
        failedList.append(testName+" for python%s"%infoMap['exactVersionShort']+" in "+serverMode+" mode failed: expected result was %s, result was %s"%(`expectedResult`, `result`))
        return 0



def checkPageResult(testName, infoMap, code, config, extraCompileOption, urlList, expectedResultList, failedList, exactResult=1, isSSL=0, extraRequestHeader=[], expectedHeaderList=[]):
    response = None
    res=compileCode(infoMap, code, extraCompileOption)
    if res.lower().find('error')!=-1:
        failedList.append(testName+" for python%s"%infoMap['exactVersionShort']+' failed: compilation failed (%s)'%res)
        print "*** FAILED ***"
    else:
        # Try it in all 3 modes (regular, threading, threadPooling) (we're missing forking and process pooling)
        modeList=[('r',''), ('t', 'threading=1'), ('tp', 'threadPool=3')]
        for mode,modeConfig in modeList:
            f=open("RootServer.cfg", "w")
            f.write(config+"\n"+modeConfig)
            f.close()

            pid=startServer(infoMap)
            passed=1
            cookies=None
            for i in range(len(urlList)):
                url=urlList[i]
                expectedResult=expectedResultList[i]
                result, cookies, response=getPage(url, cookies, isSSL, extraRequestHeader)
                if expectedHeaderList:
                    if response.status != expectedHeaderList[0]:
                        failedList.append(testName+" for python%s"%infoMap['exactVersionShort']+" in "+mode+" mode failed: expected result status was %s, result status was %s"%(expectedHeaderList[0], response.status))
                        passed=0
                        print "*** FAILED ***"
                        break
                if not checkResult(testName, infoMap, mode, result, expectedResult, failedList, exactResult):
                    passed=0
                    print "*** FAILED ***"
                    break
            shutdownServer(pid, mode, isSSL)
            if passed:
                print mode+"...",
                sys.stdout.flush()
            else: break
        if passed: print "passed"
        sys.stdout.flush()
    return response

def checkCompilerNoError(testName, infoMap, code, extraCompileOption, failedList):
    res=compileCode(infoMap, code, extraCompileOption)
    if res.lower().find('error')!=-1:
        failedList.append(testName+" for python%s"%infoMap['exactVersionShort']+' failed: compilation failed (%s)'%res)
        print "*** FAILED ***"
    else: print "passed"    

def checkInCompilerError(testName, infoMap, code, extraCompileOption, compilerErrorList, failedList):
    res=compileCode(infoMap, code, extraCompileOption)
    for compilerError in compilerErrorList:
        if res.find(compilerError)==-1:
            failedList.append(testName+" for python%s"%infoMap['exactVersionShort']+' failed: expected compilation error "%s", but compilation returned "%s"'%(compilerError, res))
            print "*** FAILED ***"
            return
    print "passed"

def checkNotInSourceFile(testName, infoMap, code, extraCompileOption, errorCodeList, failedList):
    compiledCode=getCompiledCode(testName, infoMap, code, extraCompileOption, failedList)
    if not compiledCode: return
    for errorCode in errorCodeList:
        if compiledCode.find(errorCode)!=-1:
            failedList.append(testName+" for python%s"%infoMap['exactVersionShort']+' failed: found "%s" in compiled code'%errorCode)
            print "*** FAILED ***"
            return
    print "passed"

def checkInSourceFile(testName, infoMap, code, extraCompileOption, codeList, failedList):
    compiledCode=getCompiledCode(testName, infoMap, code, extraCompileOption, failedList)
    if not compiledCode: return
    for code in codeList:
        if compiledCode.find(code)==-1:
            failedList.append(testName+" for python%s"%infoMap['exactVersionShort']+' failed: "%s" not found in compiled code'%code)
            print "*** FAILED ***"
            return
    print "passed"

def checkXmlrpcResult(testName, infoMap, code, config, extraCompileOption, urlList, funcList, expectedResultList, failedList, exactResult=1, isSSL=0):
    res=compileCode(infoMap, code, extraCompileOption)
    if res.lower().find('error')!=-1:
        failedList.append(testName+" for python%s"%infoMap['exactVersionShort']+' failed: compilation failed (%s)'%res)
        print "*** FAILED ***"
    else:
        # Try it in all 3 modes (regular, threading, threadPooling) (we're missing forking and process pooling)
        modeList=[('r',''), ('t', 'threading=1'), ('tp', 'threadPool=3')]
        for mode,modeConfig in modeList:
            f=open("RootServer.cfg", "w")
            f.write(config+"\n"+modeConfig)
            f.close()

            pid=startServer(infoMap)
            passed=1
            cookies=None
            for i in range(len(urlList)):
                url=urlList[i]
                func=funcList[i]
                expectedResult=expectedResultList[i]
                result=getXmlrpc(url, func, isSSL)
                if not checkResult(testName, infoMap, mode, result, expectedResult, failedList, exactResult):
                    passed=0
                    print "*** FAILED ***"
                    break
            shutdownServer(pid, mode, isSSL)
            if passed:
                print mode+"...",
                sys.stdout.flush()
            else: break
        if passed: print "passed"
        sys.stdout.flush()


