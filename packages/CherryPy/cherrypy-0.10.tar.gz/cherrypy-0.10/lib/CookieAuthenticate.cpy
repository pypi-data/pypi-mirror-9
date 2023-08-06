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

import md5

################
CherryClass CookieAuthenticate abstract:
################
variable:
    timeoutMessage="Session timed out"
    wrongLoginPasswordMessage="Wrong login/password"
    noCookieMessage="No cookie"
    loginCookieName="CherryLogin"
    dateCookieName="CherryDate"
    passwordCookieName="CherryPassword"
    timeout=60 # in minutes
    login = ""
aspect:
    (method.name not in ('loginScreen','logoutScreen','doLogin') and (method.type=='view' or method.type=='mask'))  and not method.isHidden start:
        if not request.simpleCookie.has_key(self.loginCookieName) or not request.simpleCookie.has_key(self.dateCookieName) or not request.simpleCookie.has_key(self.passwordCookieName):
            return self.loginScreen(self.noCookieMessage, request.browserUrl)
        _login=request.simpleCookie[self.loginCookieName].value
        _date=request.simpleCookie[self.dateCookieName].value
        _password=request.simpleCookie[self.passwordCookieName].value

        # Check that login exists
        _realPasswordList=self.getPasswordListForLogin(_login)

        # Check that date isn't too old
        _now=int(time.time())
        try: _nowCookie=int(_date)
        except: _nowCookie=0
        if not _nowCookie<=_now<=_nowCookie+self.timeout*60: return self.loginScreen(self.timeoutMessage, request.browserUrl, _login)

        # Check that password match
        _goodPassword=0
        for _realPassword in _realPasswordList:
            _clearPassword=_login+_date+_realPassword
            if md5.new(_clearPassword).hexdigest()==_password:
                _goodPassword=1
                self.login=_login
                break
        if not _goodPassword:
            self.login=""
            return self.loginScreen(self.noCookieMessage, request.browserUrl, _login)

        # Everything is okay: update cookies with new date and password values
        _newDate=str(_now)
        _newClearPassword=_login+_newDate+_realPassword
        _newPassword=md5.new(_newClearPassword).hexdigest()
        response.simpleCookie[self.dateCookieName]=_newDate
        response.simpleCookie[self.dateCookieName]['path']='/'
        response.simpleCookie[self.dateCookieName]['max-age']=31536000
        response.simpleCookie[self.dateCookieName]['version']=1
        response.simpleCookie[self.passwordCookieName]=_newPassword
        response.simpleCookie[self.passwordCookieName]['path']='/'
        response.simpleCookie[self.passwordCookieName]['max-age']=31536000
        response.simpleCookie[self.passwordCookieName]['version']=1

function:
    def getPasswordListForLogin(self, login):
        if login=='login': return ['password']
        return []
    def whoIsLoggedIn(self):
        print 'CherryWarning: whoIsLoggedIn is deprecated: use "self.login" instead'
        return self.login

view:
    def doLogin(self, login, password, fromPage):
        # Check that login/password match
        realPasswordList=self.getPasswordListForLogin(login)
        if password not in realPasswordList:
            self.login=""
            return self.loginScreen(self.wrongLoginPasswordMessage, fromPage, login)
        self.login=login
        # Set cookies
        date=str(int(time.time()))
        clearPassword=login+date+password
        password=md5.new(clearPassword).hexdigest()
        response.simpleCookie[self.loginCookieName]=login
        response.simpleCookie[self.loginCookieName]['path']='/'
        response.simpleCookie[self.loginCookieName]['max-age']=31536000
        response.simpleCookie[self.loginCookieName]['version']=1
        response.simpleCookie[self.dateCookieName]=date
        response.simpleCookie[self.dateCookieName]['path']='/'
        response.simpleCookie[self.dateCookieName]['max-age']=31536000
        response.simpleCookie[self.dateCookieName]['version']=1
        response.simpleCookie[self.passwordCookieName]=password
        response.simpleCookie[self.passwordCookieName]['path']='/'
        response.simpleCookie[self.passwordCookieName]['max-age']=31536000
        response.simpleCookie[self.passwordCookieName]['version']=1


        response.headerMap['location']=fromPage
        response.headerMap['status']=302
        return "<html><body>Nobody should see that</body></html>"
    def doLogout(self):
        response.simpleCookie[self.passwordCookieName]=""
        response.simpleCookie[self.passwordCookieName]['path']='/'
        response.simpleCookie[self.passwordCookieName]['max-age']=0
        response.simpleCookie[self.passwordCookieName]['version']=1
        response.headerMap['location']=self.getPath()+'/logoutScreen'
        response.headerMap['status']=302
        self.login=""
        return ""
    def logoutScreen(self):
        return self.loginScreen("You have been logged out", self.getPath()+'/index')

mask:
    def loginScreen(self, message, fromPage, login=''):
        <html><body>
            Message: <div py-eval="message">message</div>
            <form method="post" py-attr="self.getPath()+'/doLogin'" action="">
                Login: <input type=text name=login py-attr="login" value="" length=10><br>
                Password: <input type=password name=password length=10><br>
                <input type=hidden name=fromPage py-attr="fromPage" value=""><br>
                <input type=submit>
            </form>
        </body></html>

