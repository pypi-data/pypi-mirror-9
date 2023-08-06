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

################
CherryClass CookieSessionAuthenticate abstract:
################
variable:
    timeoutMessage="Session timed out"
    wrongLoginPasswordMessage="Wrong login/password"
    noCookieMessage="No cookie"
    logoutMessage="You have been logged out"
    sessionIdCookieName="CherrySessionId"
    timeout=60 # in minutes
aspect:
    (method.name in ('loginScreen','logoutScreen','doLogin')) start:
        request.login = ''
    (method.name not in ('loginScreen','logoutScreen','doLogin') and (method.type=='view' or method.type=='mask') and not method.isHidden) start:
        request.login = ''
        if not request.simpleCookie.has_key(self.sessionIdCookieName):
            return self.loginScreen(self.noCookieMessage, request.browserUrl)
        _sessionId=request.simpleCookie[self.sessionIdCookieName].value
        _now=time.time()

        # Check that session exists and hasn't timeout
        _timeout=0
        if not request.sessionMap.has_key(_sessionId):
            return self.loginScreen(self.noCookieMessage, request.browserUrl)
        else:
            _login, _expire=request.sessionMap[_sessionId]
            if _expire<_now: _timeout=1
            else:
                _expire=_now+self.timeout*60
                request.sessionMap[_sessionId]=_login, _expire

        if _timeout:
            return self.loginScreen(self.timeoutMessage, request.browserUrl)
        request.login = _login

function:
    def checkLoginAndPassword(self, login, password):
        if (login,password)==('login','password'): return ''
        return 'Wrong login/password'
    def whoIsLoggedIn(self):
        print 'CherryWarning: whoIsLoggedIn is deprecated: use "request.login" instead'
        return request.login

    def _generateSessionId(self, sessionIdList):
        choice="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        while 1:
            _sessionId=""
            for dummy in range(20): _sessionId+=whrandom.choice(choice)
            if _sessionId not in sessionIdList: return _sessionId


view:
    def doLogin(self, login, password, fromPage):
        # Check that login/password match
        errorMsg = self.checkLoginAndPassword(login, password)
        if errorMsg:
            request.login = ''
            return self.loginScreen(errorMsg, fromPage, login)
        request.login = login
        # Set session
        _newSessionId=self._generateSessionId(request.sessionMap.keys())
        request.sessionMap[_newSessionId]=login,time.time()+self.timeout*60
        
        response.simpleCookie[self.sessionIdCookieName]=_newSessionId
        response.simpleCookie[self.sessionIdCookieName]['path']='/'
        response.simpleCookie[self.sessionIdCookieName]['max-age']=31536000
        response.simpleCookie[self.sessionIdCookieName]['version']=1

        response.headerMap['location']=fromPage
        response.headerMap['status']=302
        return "<html><body>Nobody should see that</body></html>"
    def doLogout(self):
        try:
            _sessionId=request.simpleCookie[self.sessionIdCookieName].value
            del request.sessionMap[_sessionId]
        except: pass
        
        response.simpleCookie[self.sessionIdCookieName]=""
        response.simpleCookie[self.sessionIdCookieName]['path']='/'
        response.simpleCookie[self.sessionIdCookieName]['max-age']=0
        response.simpleCookie[self.sessionIdCookieName]['version']=1
        response.headerMap['location']=self.getPath().replace('/root','')+'/logoutScreen'
        response.headerMap['status']=302
        request.login = ''
        return ""
    def logoutScreen(self):
        return self.loginScreen(self.logoutMessage, self.getPath()+'/index')

mask:
    def loginScreen(self, message, fromPage, login=''):
        <html><body>
            Message: <py-eval="message">
            <form method="post" action="doLogin">
                Login: <input type=text name=login py-attr="login" value="" length=10><br>
                Password: <input type=password name=password length=10><br>
                <input type=hidden name=fromPage py-attr="fromPage" value=""><br>
                <input type=submit>
            </form>
        </body></html>

