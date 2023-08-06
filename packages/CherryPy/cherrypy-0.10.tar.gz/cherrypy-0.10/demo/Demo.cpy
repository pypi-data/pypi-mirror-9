use HttpAuthenticate, CookieAuthenticate, MaskTools, Form

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

def initServer():
    global hasXslt, Processor, InputSource
    hasXslt=1
    try:
        from Ft.Xml.Xslt import Processor
        from Ft.Xml import InputSource
    except: hasXslt=0


CherryClass XslTransform:
function:
    def transform(self, xslStylesheet, xmlInput):
        processor=Processor.Processor()
        sheet=InputSource.DefaultFactory.fromString(xslStylesheet, "")
        source=InputSource.DefaultFactory.fromString(xmlInput, "")
        processor.appendStylesheet(sheet)
        return processor.run(source)

CherryClass Demo:
function:
    def htmlQuote(self, data):
        entityMap=[
            ('&','&amp;'),
            ('<','&lt;'),
            ('>','&gt;'),
            ('"','&quot;')]
        for k,v in entityMap: data=data.replace(k,v)
        return data
mask:
    def index(self):
        <html>
        <head><title>CherryPy : Demo</title></head>
        <body>
        <a href="http://www.cherrypy.org"><img py-attr="request.base+'/static/cherryPyLogo.gif'" src="" border=0></a>
        <br><br>
        <b>Welcome to the CherryPy demo</b><br><br>
        <b>Below are a few examples to demonstrate a few of CherryPy's capabilities</b><br><br>
        <b>Demo: Prestation</b><br>
        Prestation is a sample site developed with CherryPy.<br>
        To demonstrate how easy it is to develop multi-skin websites with CherryPy (by deriving classes), the
        site comes in two flavours: French and English. Both use different colors and layout<br>
        The source code is provided with CherryPy.<br>
        <a py-attr="request.base+'/prestationEnglish/index'" href="">Check it out</a>
        <br><br>
        <b>Demo: CherryPy basic functionnalities</b><br>
        <a href="template">Templating language</a><br>
        <a href="oop">Using OOP to develop a web site</a><br>
        <a href="include">Using an HTML editor to edit templates</a><br>
        <a href="post">File upload</a><br>
        <a href="cookie">Cookie handling</a><br>
        <a href="sessions">Using sessions</a><br>
        <br>
        <b>Demo: CherryPy more advanced features</b><br>
        <a href="xmlXsl">Using XML/XSL</a> (based on the 4Suite module)<br>
        <a href="ssl">SSL/HTTPS support</a> (based on the PyOpenSSL module)<br>
        <a href="streaming">Using streaming</a><br>
        <br>
        <b>Demo: CherryPy standard library modules</b><br>
        <a href="testHttpAuthenticate">HTTP-based authentication</a><br>
        <a href="testCookieAuthenticate">Cookie-based Authentication</a><br>
        <a href="/testForm/index">Form handling</a><br>
        <a href="maskTools">HTML patterns</a><br>
        </body></html>
    def ssl(self):
        <html>
        <head><title>CherryPy Demo : SSL/HTTPS support</title></head>
        <body>
        <h2>SSL/HTTPS support</h2><br>
        The built-in HTTP server supports SSL (based on the PyOpenSSL module).<br>
        Check out <a href="http://www.cherrypy.org/static/html/howto/node10.html">this HowTo</a>
        to learn how to configure the HTTP server to run in SSL mode.<br><br>
        Click on the following link to browse the CherryPy.org website in SSL mode:
        <a href="https://www.cherrypy.org">https://www.cherrypy.org</a>.<br>
        PS: Since the certificate we're using
        is not signed, your browser will open a window to ask you if you want to proceed... Just say yes
    def streaming(self):
        <html>
        <head><title>CherryPy Demo : Using streaming</title></head>
        <body>
        <h2>Using streaming</h2><br>
        If one of your page is really big or if it takes a long time to build, then it might be a good option to use
        streaming, which means that the page will be returned to the browser in chunks.<br>
        The following code shows how to use streaming.<br>
        <py-eval="self.viewCode(self.streamingCode())">
        <br>
        Click <a href="streamingResult">here</a> to see the result.
        </body></html>
view:
    def streamingResult(self):
        import time
        response.wfile.write("HTTP/1.0 200\r\n")
        response.wfile.write("Content-Type: text/html\r\n\r\n")
        response.wfile.write("<html><body>\n")
        response.wfile.write("First line. Sleeping 2 seconds ...<br>")
        response.wfile.write("<!-- " + "X"* 200 + "-->") # To force IE to display beginning of page
        time.sleep(2)
        response.wfile.write("Second line. Sleeping 2 seconds ...<br>")
        time.sleep(2)
        response.wfile.write("Third and last line")
        response.wfile.write("</body></html>")
        response.sendResponse = 0
        return "" # The view still needs to return a string
mask:
    def template(self):
        <html>
        <head><title>CherryPy Demo : Templating language</title></head>
        <body>
        <h2>Templating language</h2><br>
        CHTL and CGTL are CherryPy's templating languages. They're very easy to learn and easy to use (they're only
        composed of a few tags), and yet they're very powerful.<br>
        Moreover, CHTL is HTML-editor-safe, which means that pages can go back and forth between developers and designers !
        <br>The following code is an example that displays a table with all web colors:<br>
        <py-eval="self.viewCode(self.webColorCode())">
        <br>
        Result:<br><br>
        <py-exec="codeList=['00', '33', '66', '99', 'CC', 'FF']">
        <table border=1>
        <py-for="r in codeList">
            <py-for="g in codeList">
                <tr>
                    <py-for="b in codeList">
                        <py-exec="color='#%s%s%s'%(r,g,b)">
                        <td py-attr="color" bgColor="" py-eval="'&nbsp;&nbsp;'+color+'&nbsp;'"></td>
                    </py-for>
                </tr>
            </py-for>
        </py-for>
        </table>
        </body></html>
    def include(self):
        <html>
        <head><title>CherryPy Demo : Using an HTML editor to edit templates</title></head>
        <body>
        <h2>Using an HTML editor to edit templates</h2><br>
        CHTL (one of the 2 templating languages) is HTML-editor-safe. This means that webdesigners can use their favorite
        HTML editor (Dreamweaver, Amaya, ...) to edit the files.<br>
        Normally, templates (or "masks") are stored in CherryPy source files, with the rest of the code. But we know that
        webdesigners like to work on their own files, so CherryPy provides a way to do that, using the <i><py-eval="'&lt;py-'+'include&gt;'"></i> tag.<br>
        Example:<br><br>
        <b>header.html: (can be edited by webdesigners with an HTML editor)</b>
        <py-eval="self.viewCode(self.headerTemplateCode())">
        <br>
        <b>footer.html: (can be edited by webdesigners with an HTML editor)</b>
        <py-eval="self.viewCode(self.footerTemplateCode())">
        <br>
        <b>index.html: (can be edited by webdesigners with an HTML editor)</b>
        <py-eval="self.viewCode(self.indexTemplateCode())">
        <br>
        <b>Hello.cpy: (only edited by developers)</b>
        <py-eval="self.viewCode(self.indexCherryTemplateCode())">
        <br>
        Result:<br><br>
        Hi, I'm the header. I'll be almost the same for all pages of the site. This will provide a constant look for the site.<br>
        By the way, the time on the server is: <b py-eval="time.time()">time</b><br><br>
        Hello, <b>John</b> !<br>
        Do you like cherry pie ?
        <br><br>Hi, I'm the footer
        </body></html>
    def oop(self):
        <html>
        <head><title>CherryPy Demo : Using OOP to develop a web site</title></head>
        <body>
        <h2>Using OOP to develop a web site:</h2><br>
        Using Object Oriented Programming for your web site works very well in the following cases:
        <ul>
        <li>You have different parts of your web site that use the same functionality but applied to a different kind of data</li>
        <li>You need to display the same things on several pages, but you have to change the design or the order of the modules</li>
        </ul>
        Let's take an example: you want to build a web site where you sell books, DVDs and video games. You'll have
        3 different modules in your site, but they'll all use the same functionalities: search an item, view it, buy it, ...<br>
        In this case, all you have to do is declare a generic class that implements the common features, and then sub-class
        it for each item type. Each of the sub-classes will only implement what is really specific to that item type.<br>
        <br><br>
        Here is what the hierarchy will look like:<br><br>
        <center>
        <table border=0><tr><td colspan=5 align=center>
        <b>GenericStore</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
        (parent class for all item types)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        </td></tr>
        <tr><td align=center>|<br>|<br><b>BookStore</b>
        </td><td width=10>&nbsp;</td><td align=center>|<br>|<br><b>DvdStore</b>
        </td><td width=10>&nbsp;</td><td align=center>|<br>|<br><b>VideoGameStore</b>
        </td></tr></table>
        </center>
        <br><br>
        Here is how it's done with CherryPy:<br>
        <py-eval="self.viewCode(self.oopCode())">
        <br><br>
        Click <a href="/genericStore/index">here</a> to see the result
        </body></html>
    def cookie(self, addOrRemove=''):
        <html>
        <head><title>CherryPy Demo : Cookie handling</title></head>
        <body>
        <h2>Cookie handling:</h2><br>
        Handling cookies is a very easy task with CherryPy.<br>
        When a browser sends a cookie, CherryPy automatically builds a SimpleCookie object containing the cookie
        information. That object is called <i>request.simpleCookie</i>.<br>
        If you want to send back a cookie to the browser, all you have to do is use <i>response.simpleCookie</i>.<br>
        The following code allows you to display the cookies that are sent by the browser and to send back some cookies:<br>
        <py-eval="self.viewCode(self.cookieCode())">
        <br><br>
        Result:<br><br>
        Value of simpleCookie: <py-eval="request.simpleCookie"><br>
        Click <a href="cookie?addOrRemove=add">here</a> once to set the cookies and twice to see them in <i>simpleCookie</i><br>
        Click <a href="cookie?addOrRemove=remove">here</a> once to remove the cookies and twice to see it in <i>simpleCookie</i>
        </body></html>
        <py-if="addOrRemove=='add'">
            <py-code="
                response.simpleCookie['cookieName']='cookieValue'
                response.simpleCookie['cookieName']['path']='/'
                response.simpleCookie['cookieName']['max-age']=3600
                response.simpleCookie['cookieName']['version']=1
            ">
            <py-code="
                response.simpleCookie['cookieName2']='cookieValue2'
                response.simpleCookie['cookieName2']['path']='/'
                response.simpleCookie['cookieName2']['max-age']=3600
                response.simpleCookie['cookieName2']['version']=1
            ">
        </py-if>
        <py-if="addOrRemove=='remove'">
            <py-code="
                response.simpleCookie['cookieName']=''
                response.simpleCookie['cookieName']['path']='/'
                response.simpleCookie['cookieName']['max-age']=0
                response.simpleCookie['cookieName']['version']=1
            ">
            <py-code="
                response.simpleCookie['cookieName2']=''
                response.simpleCookie['cookieName2']['path']='/'
                response.simpleCookie['cookieName2']['max-age']=0
                response.simpleCookie['cookieName2']['version']=1
            ">
        </py-if>
    def sessions(self):
        <html>
        <head><title>CherryPy Demo : Using sessions</title></head>
        <body>
        <h2>Using sessions:</h2><br>
        Sessions are now a built-in feature of CherryPy. You can store session data to RAM, to disk, to a database or anywhere you want (CherryPy allows you to write your own custom methods to store session data if you want).<br>
        The way it works is very easy: CherryPy just makes a dictionary available in your code were you can store/retrieve
        session data. This dictionary is called <b>request.sessionMap</b>.<br><br>
        The following code implements a trivial page counter:<br>
        <py-eval="self.viewCode(self.sessionsCode())">
        <br><br>
        Result:<br><br>
        <py-code="
            count=request.sessionMap.get('pageViews', 0)+1
            request.sessionMap['pageViews']=count
        ">
        Hello, you've been here <py-eval="count"> time(s).<br>
        Refresh this page to increment the counter.<br>
        If you close your browser or stop accessing this site for an hour, your session data will expire and the counter
        will be reset.<br>
        Your session ID is: <py-eval="request.sessionMap['_sessionId']">
    def post(self):
        <html>
        <head><title>CherryPy Demo : File upload</title></head>
        <body>
        <h2>File upload:</h2><br>
        With CherryPy, all values entered in a form are converted to a Python string and passed to a method as
        regular arguments. It doesn't matter if it's a GET or a POST, or if the values are a short string or a
        big file that's being uploaded. It's all transparent to the developer.<br>
        The following code shows how a text string and a file upload are handled:<br>
        <br>Form code:
        <py-eval="self.viewCode(self.postFormCode())">
        <br>Action method code:
        <py-eval="self.viewCode(self.postFormActionCode())">
        <br>
        Result:<br><br>
            Enter your name and a photo:
            <form method=post action=postFile enctype="multipart/form-data">
                Name: <input name=name><br>
                Photo: <input type=file name=photo><br>
                <input type=submit>
            </form>
        </body></html>
    def postFile(self, name, photo):
        <html><body>
            Name: <py-eval="name"><br>
            Size of the photo: <py-eval="len(photo)"> bytes<br>
            Filename of the photo: <py-eval="request.filenameMap['photo']"><br>
            Mime type of the photo: <py-eval="request.fileTypeMap['photo']">
        </body></html>
    def testHttpAuthenticate(self):
        <html>
        <head><title>CherryPy Demo : HTTP-based authentication</title></head>
        <body>
        <h2>HTTP-based authentication:</h2><br>
        CherryPy comes with a standard module for HTTP-based authentication.<br>
        It is very easy to use. All you have to do is create a CherryClass that inherits from that module, and implement
        the <i>getPasswordListForLogin</i> method to specify what allowed logins/passwords are:<br>
        <py-eval="self.viewCode(self.httpAuthenticateCode())">
        <br><br>
        Result:<br><br>
        Click <a href="/httpProtected/index">here</a> and you will be prompted for a login and a password. Enter "login" and "password" to view the next screen.
        </body></body>
    def testCookieAuthenticate(self):
        <html>
        <head><title>CherryPy Demo : Cookie-based authentication</title></head>
        <body>
        <h2>Cookie-based authentication:</h2><br>
        CherryPy comes with a standard module for Cookie-based authentication.<br>
        It is very easy to use. All you have to do is create a CherryClass that inherits from that module, and implement
        the <i>getPasswordListForLogin</i> method to specify what allowed logins/passwords are. Unlike many
        Cookie-based authentication schemes, it doesn't require any database to store the session informations. These
        informations are encrypted and then stored in a cookie:<br>
        <py-eval="self.viewCode(self.cookieAuthenticateCode())">
        <br><br>
        Result:<br><br>
        Click <a href="/cookieProtected/index">here</a> and you will be prompted for a login and a password. Enter "login" and "password" to view the next screen.
        </body></body>
    def maskTools(self):
        <html>
        <head><title>CherryPy Demo : HTML patterns</title></head>
        <body>
        <h2>HTML patterns</h2><br>
        With CherryPy, it is easy to create masks that are used to render commonly used patterns on HTML pages. For instance:
        text inside a box, list displayed on several columns or lines, ...<br>
        CherryPy comes with a module called <i>MaskTools</i> that contains a few of those, but you can also easily create
        your own masks.<br>
        The following code uses the <i>MaskTools</i> module:<br>
        <py-eval="self.viewCode(self.maskToolsCode())">
        <br>Result:<br><br>
        <py-eval="maskTools.textInBox('This is some text displayed in a red box filled with yellow', boxColor='red', insideColor='yellow')">
        <br>
        Display integers from 1 to 102 in 7 columns with 20 pixels between each column:
        <py-eval="maskTools.displayByColumn(map(str,range(1,103)), 7, 0, 20)">
        <br>
        Display integers from 1 to 102 in 7 lines with 5 pixels between each line:
        <py-eval="maskTools.displayByLine(map(str,range(1,103)), 7, 0, 5)">
        </body></body>
    def xmlXsl(self):
        <py-code="
            if not hasXslt:
                return """
                    <html><body>
                    <h2>Using XML/XSL</h2><br>
                    <b>This demo requires the 4Suite package to be installed on your machine !</b><br>
                    It looks like this package is not installed.<br>
                    Check out the CherryPy "HowTo" documentation for information about using XML/XSL with CherryPy.<br>
                    This documentation is available at <a href='http://www.cherrypy.org/static/html/howto/index.html'>http://www.cherrypy.org/static/html/howto/index.html</a>
                    </body></html>
                """    
        ">
        <html>
        <head><title>CherryPy Demo : Using XML/XSL</title></head>
        <body>
        <h2>Using XML/XSL</h2><br>
        With CherryPy, it is very easy to use XML/XSL to develop you website.<br><br>
        <a href="xmlXslSample">Click here</a> to see some sample code that demonstrates how to do it, or<br>
        <a href="xmlXslOnline">Click here</a> to use an online tool that lets you input an XML document and
        an XSL stylesheet and then displays the result of the transformation.<br>
        This online tool has been written with only a few lines of codes of CherryPy ...
        </body></html>
    def xmlXslSample(self):
        <html>
        <head><title>CherryPy Demo : XML/XSL example</title></head>
        <body>
        <h2>XML/XSL example</h2><br>
        The following demonstrates how to use XML/XSL in CherryPy. In real life, the XML document would probably be generated
        by a function or a view, based on some data coming from a database or some other ressource:<br>
        (Note that it seems that the 4Suite API has changed again in the latest releases, so you might have to tweak this code if you're using a recent release).<br>
        <py-eval="self.viewCode(self.xmlXslSampleCode())">
        <br>Result:<br><br>
        <py-eval="xslTransform.transform(self.xslStylesheet(), self.xmlInput())">
        </body></body>
    def xslStylesheet(self):
        <?xml version="1.0" encoding="ISO-8859-1"?>

        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

        <xsl:template match="/">
            <html><body>
                <h2>My CD Collection</h2>
                <table border="1">
                    <tr bgcolor="#9acd32">
                        <th align="left">Title</th>
                        <th align="left">Artist</th>
                    </tr>
                    <xsl:for-each select="catalog/cd">
                        <tr>
                            <td><xsl:value-of select="title"/></td>
                            <td><xsl:value-of select="artist"/></td>
                        </tr>
                    </xsl:for-each>
                </table>
            </body></html>
        </xsl:template>

        </xsl:stylesheet> 
    def xmlInput(self):
        <?xml version="1.0" encoding="ISO-8859-1"?>
        <catalog>
            <cd>
                <title>Empire Burlesque</title>
                <artist>Bob Dylan</artist>
            </cd>
            <cd>
                <title>Hide your heart</title>
                <artist>Bonnie Tyler</artist>
            </cd>
        </catalog>
    def xmlXslOnline(self, xmlDocument="", xslStylesheet="", width=55, changeWidth=0):
        <html><head><title>CherryPy Demo : Online XML/XSL transformation tool</title></head><body>
        <h2>Online XML/XSL transformation tool</h2>
        <table border=0><tr>
        <td>
            The following tool lets you enter an XML document, an XSL stylesheet, and it shows the result of the transformation.<br>
            This tool has been written with only a few lines of <a py-attr="request.base" href="">CherryPy</a> code and it uses the <a href="http://4suite.org">4Suite module</a>.<br>
            Source code is available <a py-attr="self.getPath()+'/xmlXslOnlineViewCode'" href="">here</a>.<br><br>
        </td>
        <td width=50>&nbsp;</td>
        <td valign=middle>
            <a py-attr="request.base" href=""><img py-attr="request.base+'/static/poweredByCherryPy.gif'" src="" border=0 alt="Powered by CherryPy"></a>
        </td>
        </table>
        <form name="xmlForm" action="xmlXslOnline" method="post" style="margin-top: 0; margin-bottom: 0">
        <table border=0 width="100%">
            <py-if="int(width)<=55">
                # Side by side
                <tr>
                    <td align=center><b>XML document:</b>
                    <td width=50>&nbsp;</td>
                    <td align=center><b>XSL stylesheet:</b>
                </tr>
                <tr>
                    <td align=center>
                        <textarea name=xmlDocument rows=15 py-attr="width" cols=""><py-code="
                                if xmlDocument: _page.append(self.htmlQuote(xmlDocument))
                                else: _page.append(self.htmlQuote(self.xmlInput().replace('\t','  ')))
                            "></textarea>
                    </td>
                    <td width=50>&nbsp;</td>
                    <td align=center>
                        <textarea name=xslStylesheet rows=15 py-attr="width" cols=""><py-code="
                                if xmlDocument: _page.append(self.htmlQuote(xslStylesheet))
                                else: _page.append(self.htmlQuote(self.xslStylesheet().replace('\t','  ')))
                            "></textarea>
                    </td>
                </tr>
                <tr><td colspan=3 align=center><br>
                    <input type=submit value="Narrower textareas" onClick="document.xmlForm.width.value='<py-eval="int(width)-20">';document.xmlForm.changeWidth.value='1';return true;">
                    <input type=submit value="Run transformation">
                    <input type=submit value="Wider textareas" onClick="document.xmlForm.width.value='<py-eval="int(width)+20">';document.xmlForm.changeWidth.value='1';return true;">
                </td></tr>
            </py-if><py-else>
                # One above the other
                <tr><td align=center>
                    <b>XML document:</b><br>
                    <textarea name=xmlDocument rows=15 py-attr="width" cols=""><py-code="
                            if xmlDocument: _page.append(self.htmlQuote(xmlDocument))
                            else: _page.append(self.htmlQuote(self.xmlInput().replace('\t','  ')))
                        "></textarea>
                    <br><br>
                    <b>XSL stylesheet:</b><br>
                    <textarea name=xslStylesheet rows=15 py-attr="width" cols=""><py-code="
                            if xmlDocument: _page.append(self.htmlQuote(xslStylesheet))
                            else: _page.append(self.htmlQuote(self.xslStylesheet().replace('\t','  ')))
                        "></textarea>
                </td></tr>
                <tr><td align=center><br>
                    <input type=submit value="Narrower textareas" onClick="document.xmlForm.width.value='<py-eval="int(width)-20">';document.xmlForm.changeWidth.value='1';return true;">
                    <input type=submit value="Run transformation">
                    <input type=submit value="Wider textareas" onClick="document.xmlForm.width.value='<py-eval="int(width)+20">';document.xmlForm.changeWidth.value='1';return true;">
                </td></tr>
            </py-else>
        </table>
        <input type=hidden name=width py-attr="width" value="">
        <input type=hidden name=changeWidth value="0">
        </form>
        <py-if="xmlDocument and xslStylesheet and int(changeWidth)==0">
            <py-code="
                try:
                    result=xslTransform.transform(xslStylesheet, xmlDocument)
                except:
                    import traceback, StringIO
                    _page.append("<font color=red>An error occured during the transformation:<br>")
                    bodyFile=StringIO.StringIO()
                    traceback.print_exc(file=bodyFile)
                    errorBody=bodyFile.getvalue()
                    bodyFile.close()
                    _page.append(errorBody.replace('\n','<br>').replace(' ','&nbsp;&nbsp;'))
                    _page.append("</font></body></html>")
                    return "".join(_page)
            ">
            <b>Html result:</b><br><br>
                <font face=arial size=2 color=navy>
                <py-eval="self.htmlQuote(result).replace('\n','<br>').replace(' ','&nbsp;&nbsp;')">
                </font>
            <br><br><b>Rendered html result:</b><br><br>
                <py-eval="result">
        </py-if>
        </body></body>

    def xmlXslOnlineViewCode(self):
        Here is the source code for the online XML/XSL transformation tool. This code must be compiled with <a py-attr="request.base" href="">CherryPy</a>.<br>
        <py-eval="self.viewCode(self.xmlXslOnlineCode())">


view:
    def viewCode(self, code):
        code=code.replace('&','&amp;')
        code=code.replace('>','&gt;').replace('<','&lt;').replace('\t','&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;').replace(' ','&nbsp;').replace('\n','<br>')
        code=code.replace('$#', '#')
        for tag in ['py-eval', 'py-exec', 'py-code', 'py-attr', 'py-if', 'py-else', 'py-for', 'py-debug']:
            i=-20
            while 1:
                i=code.find(tag, i+20)
                if i==-1: break
                if code[i+len(tag)]=='=':
                    if tag=="py-exec": j=code.find('"&gt;', i+len(tag)+2)
                    else: j=code.find('"', i+len(tag)+2)
                    code=code[:i]+'<font color=red>'+tag+'</font>=<font color=green>'+code[i+len(tag)+1:j+1]+'</font>'+code[j+1:]
                else:
                    code=code[:i]+'<font color=red>'+tag+'</font>'+code[i+len(tag):]
        code='<font face=arial size=2 color=navy>'+code+'</font>'
        code=code.replace('$$','')
        return code

    def streamingCode(self):
        return '''
        CherryClass Root:
        view:
            def index(self):
                import time
                response.wfile.write("HTTP/1.0 200\\r\\n")
                response.wfile.write("Content-Type: text/html\\r\\n\\r\\n")
                response.wfile.write("<html><body>\\n")
                response.wfile.write("First line. Sleeping 2 seconds ...<br>")
                response.wfile.write("<!-- " + "X"* 200 + "-->") # To force IE to display beginning of page
                time.sleep(2)
                response.wfile.write("Second line. Sleeping 2 seconds ...<br>")
                time.sleep(2)
                response.wfile.write("Third and last line")
                response.wfile.write("</body></html>")
                response.sendResponse = 0
                return "" # The view still needs to return a string
        '''

    def headerTemplateCode(self):
        return """
        <html><body>
            Hi, I'm the header. I'll be almost the same for all pages of the site. This will provide a constant look for the site.<br>
            By the way, the time on the server is: <b py-eval="time.time()">time</b><br><br>
        """
    def footerTemplateCode(self):
        return """
            <br><br>Hi, I'm the footer
        </body></html>
        """
    def indexTemplateCode(self):
        return """
        <div py-include="header.html">Header</div>
            Hello, <b py-eval="name">name</b> !<br>
            Do you like cherry pie ?
        <div py-include="header.html">Footer</div>
        """

    def indexCherryTemplateCode(self):
        return """
        CherryClass Root:
        mask:
            def index(self, name='John'):
                <py-include="index.html">
        """

    def oopCode(self):
        return """
        def initServer():
            genericStore.itemList=[bookStore, dvdStore, videoGameStore]
        $$
        $########################
        CherryClass GenericStore:
        $########################
        mask:
            $# Home page: display the list of item types and let the user choose one
            def index(self):
                <html><body><center><br><br><br>
                    Welcome to the store. Choose what you want to buy:<br><br>
                    <table cellspacing=10><tr>
                    <py-for="itemType in self.itemList">
                        <td py-attr="itemType.color" bgcolor="">
                            <a py-attr="itemType.getPath()+'/viewList'" href="" py-eval="itemType.label+'s'"></a>
                        </td>
                    </py-for>
                    </tr></table>
                </center></body></html>
            def viewList(self):
                <html><body><center><br><br><br>
                <b py-eval="self.label.upper()+'S'"></b><br><br>
                Click on a <py-eval="self.label"> title to view it:<br><br>
                <table py-attr="self.color" bgcolor="" cellpadding=5>
                    <py-for="item in self.itemList">
                        <tr><td><a py-attr="self.getPath()+'/viewItem?itemIndex=%s'%_index" href="" py-eval="item[0]"></a></td></tr>
                    </py-for>
                </table>
                </center></body></html>
            $# Default viewItem mask (used for DVDs and Video games). Will be overwritten for books
            def viewItem(self, itemIndex):
                <py-exec="title, price=self.itemList[int(itemIndex)]">
                <html><body><center><br><br><br>
                    <table py-attr="self.color" bgcolor="" cellpadding=5>
                        <tr><td>Title: <py-eval="title"></td></tr>
                        <tr><td>Price: <py-eval="price">$</td></tr>
                    </table>
                </center></body></html>
        $$
        $########################
        CherryClass BookStore(GenericStore):
        $########################
        variable:
            label='book'
            color='pink'
            itemList=[('Harry Potter and the Goblet of Fire', '18', 'J. K. Rowling'), ('I love CherryPy', '5', 'Remi Delon')]
        mask:
            $# We have to overwrite viewItem for books, because we have to display the author too
            def viewItem(self, itemIndex):
                <py-exec="title, price, author=self.itemList[int(itemIndex)]">
                <html><body><center><br><br><br>
                    <table py-attr="self.color" bgcolor="" cellpadding=5>
                        <tr><td>Title: <py-eval="title"></td></tr>
                        <tr><td>Price: <py-eval="price">$</td></tr>
                        <tr><td>Author: <py-eval="author"></td></tr>
                    </table>
                </center></body></html>
        $$
        $########################
        CherryClass DvdStore(GenericStore):
        $########################
        variable:
            label='DVD'
            color='red'
            itemList=[('Star Wars Episode 1', '25'), ('The Legend of CherryPy', '4')]
        $$
        $########################
        CherryClass VideoGameStore(GenericStore):
        $########################
        variable:
            label='video game'
            color='yellow'
            itemList=[('Cool Rider 3', '29'), ('CherryPy Eating Contest', '7')]
        """

    def httpAuthenticateCode(self):
        return """
        CherryClass HttpProtected(HttpAuthenticate):
        function:
            def getPasswordListForLogin(self, login):
                if login=="login": return ["password"]    
                return []
        mask:
            def index(self):
                <html><body>You're in, your login is: <py-eval="self.login"></body></html>
        """
    def cookieAuthenticateCode(self):
        return """
        CherryClass CookieProtected(CookieAuthenticate):
        function:
            def getPasswordListForLogin(self, login):
                if login=="login": return ["password"]    
                return []
        mask:
            def index(self):
                <html><body>You're in, your login is: <py-eval="self.login"></body></html>
        """

    def sessionsCode(self):
        return """
        <py-code="
            count=request.sessionMap.get('pageViews', 0)+1
            request.sessionMap['pageViews']=count
        ">
        Hello, you've been here <py-eval="count"> time(s).<br>
        Refresh this page to increment the counter.<br>
        If you close your browser or stop accessing this site for an hour, your session data will expire and the counter
        will be reset.<br>
        Your session ID is: <py-eval="request.sessionMap['_sessionId']">
        """

    def cookieCode(self):
        return """
        def cookie(self, addOrRemove=''):
            Value of simpleCookie: <py-eval="request.simpleCookie"><br>
            Click <a href="cookie?addOrRemove=add">here</a> once to set the cookies and twice to see them in <i>simpleCookie</i><br>
            Click <a href="cookie?addOrRemove=remove">here</a> once to remove the cookies and twice to see it in <i>simpleCookie</i>
            </body></html>
        <py-if="addOrRemove=='add'">
            <py-code="
                response.simpleCookie['cookieName']='cookieValue'
                response.simpleCookie['cookieName']['path']='/'
                response.simpleCookie['cookieName']['max-age']=3600
                response.simpleCookie['cookieName']['version']=1
            ">
            <py-code="
                response.simpleCookie['cookieName2']='cookieValue2'
                response.simpleCookie['cookieName2']['path']='/'
                response.simpleCookie['cookieName2']['max-age']=3600
                response.simpleCookie['cookieName2']['version']=1
            ">
        </py-if>
        <py-if="addOrRemove=='remove'">
            <py-code="
                response.simpleCookie['cookieName']=''
                response.simpleCookie['cookieName']['path']='/'
                response.simpleCookie['cookieName']['max-age']=0
                response.simpleCookie['cookieName']['version']=1
            ">
            <py-code="
                response.simpleCookie['cookieName2']=''
                response.simpleCookie['cookieName2']['path']='/'
                response.simpleCookie['cookieName2']['max-age']=0
                response.simpleCookie['cookieName2']['version']=1
            ">
        </py-if>
        """

    def formCode(self):
        return """
        CherryClass TestForm(Form):
        function:
            def __init__(self):
                headerSep=FormSeparator('', defaultFormMask.defaultHeader)
                textField=FormField(label='Text field:', name='textField', mandatory=1, typ='text')
                textareaField=FormField(label='Textarea field:', name='textareaField', mandatory=1, typ='textarea', size='30x5')
                selectField=FormField(label='Select field:', name='selectField', mandatory=1, typ='select', optionList=['Option 1', 'Option 2', 'Option 3'])
                radioField=FormField(label='Radio field:', name='radioField', mandatory=1, typ='radio', optionList=['Option 1', 'Option 2', 'Option 3'])
                checkboxField=FormField(label='Checkbox field:', name='checkField', mandatory=0, typ='checkbox', optionList=['Option 1', 'Option 2', 'Option 3'])
                submitField=FormField(label='', name='Submit', typ='submit')
                footerSep=FormSeparator('', defaultFormMask.defaultFooter)

                self.fieldList=[headerSep, textField, textareaField, selectField, radioField, checkboxField, submitField, footerSep]

        mask:
            def index(self, **kw):
                <html><body>
                    Fill out the form and hit "Submit". If you forget any mandatory fields, the form will
                    be displayed again, and the errors will be indicated:<br>
                    <py-eval="self.formView(0)">
                </html><body>
        view:
            def postForm(self, **kw):
                if self.validateForm():
                    res="<html><body>"
                    for key, value in kw.items():
                        res+="%s : %s <br>"%(key, value)
                    return res+"</body></html>"
                else:
                    return "<html><body><font color=red>Fill out missing fields</font>"+self.formView(1)+"</body></html>"
        """

    def postFormCode(self):
        return """
        Enter your name and a photo:
        <form method=post action=postFile enctype="multipart/form-data">
            Name: <input name=name><br>
            Photo: <input type=file name=photo><br>
            <input type=submit>
        </form>
        """
    def postFormActionCode(self):
        return """
        def postFile(self, name, photo):
            <html><body>
                Name: <py-eval="name"><br>
                Size of the photo: <py-eval="len(photo)"> bytes<br>
                Filename of the photo: <py-eval="request.filenameMap['photo']"><br>
                Mime type of the photo: <py-eval="request.fileTypeMap['photo']">
            </body></html>
        """
    def webColorCode(self):
        return """
        <py-exec="codeList=['00', '33', '66', '99', 'CC', 'FF']">
        <table border=1>
        <py-for="r in codeList">
            <py-for="g in codeList">
                <tr>
                    <py-for="b in codeList">
                        <py-exec="color='#%s%s%s'%(r,g,b)">
                        <td py-attr="color" bgColor="" py-eval="'&nbsp;&nbsp;'+color+'&nbsp;'"></td>
                    </py-for>
                </tr>
            </py-for>
        </py-for>
        </table>
        """
    def maskToolsCode(self):
        return """
        <py-eval="maskTools.textInBox('This is some text displayed in a red box filled with yellow', boxColor='red', insideColor='yellow')">
        <br>
        Display integers from 1 to 102 in 7 columns with 20 pixels between each column:
        <py-eval="maskTools.displayByColumn(map(str,range(1,103)), 7, 0, 20)">
        <br>
        Display integers from 1 to 102 in 7 lines with 5 pixels between each line:
        <py-eval="maskTools.displayByLine(map(str,range(1,103)), 7, 0, 5)">
        """
    def xmlXslSampleCode(self):
        return """
        from Ft.Xml.Xslt.Processor import Processor
        $$
        CherryClass XslTransform:
        function:
            def transform(self, xslStylesheet, xmlInput):
                processor = Processor()
                processor.appendStylesheetString(xslStylesheet)
                return processor.runString(xmlInput, 0, {})
        $$
        CherryClass Root:
        view:
            def index(self):
                return xslTransform.transform(self.xslStylesheet(), self.xmlInput())
        mask:
            def xslStylesheet(self):
                <?xml version="1.0" encoding="ISO-8859-1"?>
                <xsl:stylesheet version="1.0"
                    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
                <xsl:template match="/">
                    <html><body>
                        <h2>My CD Collection</h2>
                        <table border="1">
                            <tr bgcolor="#9acd32">
                                <th align="left">Title</th>
                                <th align="left">Artist</th>
                            </tr>
                            <xsl:for-each select="catalog/cd">
                                <tr>
                                    <td><xsl:value-of select="title"/></td>
                                    <td><xsl:value-of select="artist"/></td>
                                </tr>
                            </xsl:for-each>
                        </table>
                    </body></html>
                </xsl:template>
                </xsl:stylesheet> 
            def xmlInput(self):
                <?xml version="1.0" encoding="ISO-8859-1"?>
                <catalog>
                    <cd>
                        <title>Empire Burlesque</title>
                        <artist>Bob Dylan</artist>
                    </cd>
                    <cd>
                        <title>Hide your heart</title>
                        <artist>Bonnie Tyler</artist>
                    </cd>
                </catalog>
        """
    def xmlXslOnlineCode(self):
        return """
        from Ft.Xml.Xslt.Processor import Processor
        $$
        CherryClass Root:
        function:
            $$
            $#################################################
            $# Function to escape special characters in textareas
            $#################################################
            def htmlQuote(self, data):
                entityMap={
                    '&':'&amp;',
                    '<':'&lt;',
                    '>':'&gt;',
                    '"':'&quot;'}
                for k,v in entityMap.items(): data=data.replace(k,v)
                return data
            $$
            $#################################################
            $# Function to perform transformation: only 3 lines of code !
            $#################################################
            def transform(self, xslStylesheet, xmlInput):
                processor = Processor()
                processor.appendStylesheetString(xslStylesheet)
                return processor.runString(xmlInput, 0, {})
        $$
        mask:
            $$
            $#################################################
            $# Main function: display textareas and result
            $#################################################
            def xmlXslOnline(self, xmlDocument="", xslStylesheet=""):
                <html><head><title>Online XML/XSL transformation tool</title></head><body>
                <h2>Online XML/XSL transformation tool</h2>
                <table border=0><tr>
                <td>
                    The following tool lets you enter an XML document, an XSL stylesheet, and it shows the result of the transformation.<br>
                    This tool has been written with only a few lines of <a py-attr="request.base" href="">CherryPy</a> code
                    and it uses the <a href="http://4suite.org">4Suite module</a>.<br>
                    The source code is available <a py-attr="self.getPath()+'/xmlXslOnlineSourceCode'" href="">here</a><br><br>
                </td>
                <td width=50>&nbsp;</td>
                <td valign=middle>
                    <a py-attr="request.base" href=""><img py-attr="request.base+'/static/poweredByCherryPy.gif'" src="" border=0 alt="Powered by CherryPy"></a>
                </td>
                </table>
                <form action="xmlXslOnline" method="post" style="margin-top: 0; margin-bottom: 0">
                <table border=0>
                <tr>
                    <td align=center><b>XML document:</b>
                    <td width=50>&nbsp;</td>
                    <td align=center><b>XSL stylesheet:</b>
                </tr>
                <tr>
                    <td align=center>
                        <textarea name=xmlDocument rows=15 cols=55><py-code="
                            if xmlDocument: _page.append(self.htmlQuote(xmlDocument))
                            else: _page.append(self.htmlQuote(self.xmlInput().replace('\\t','  ')))
                        "></textarea>
                    </td>
                    <td width=50>&nbsp;</td>
                    <td align=center>
                        <textarea name=xslStylesheet rows=15 cols=55><py-code="
                            if xmlDocument: _page.append(self.htmlQuote(xslStylesheet))
                            else: _page.append(self.htmlQuote(self.xslStylesheet().replace('\\t','  ')))
                        "></textarea>
                    </td>
                </tr>
                <tr><td colspan=3 align=center><br><input type=submit value="Run transformation"></td></tr>
                </table>
                </form>
                <py-if="xmlDocument and xslStylesheet">
                    <py-code="
                        error=0
                        try: result=self.transform(xslStylesheet, xmlDocument)
                        except: error=1
                    ">
                    <py-if="error==1">
                        <font color=red>An error occured during the transformation:<br>
                        <py-code="
                            import traceback, StringIO
                            bodyFile=StringIO.StringIO()
                            traceback.print_exc(file=bodyFile)
                            errorBody=bodyFile.getvalue()
                            bodyFile.close()
                            _page.append(errorBody.replace('\\n','<br>').replace(' ','&nbsp;&nbsp;'))
                        ">
                        </font>
                    </py-if><py-else>
                        <b>Html result:</b><br><br>
                            <font face=arial size=2 color=navy>
                            <py-eval="self.htmlQuote(result).replace('\\n','<br>').replace(' ','&nbsp;&nbsp;')">
                            </font>
                        <br><br><b>Rendered html result:</b><br><br>
                            <py-eval="result">
                    </py-else>
                </py-if>
                </body></body>
            $$
            $$
            $#################################################
            $# Sample XML document and XSL stylesheet
            $#################################################
            def xslStylesheet(self):
                <?xml version="1.0" encoding="ISO-8859-1"?>
        
                <xsl:stylesheet version="1.0"
                    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        
                <xsl:template match="/">
                    <html><body>
                        <h2>My CD Collection</h2>
                        <table border="1">
                            <tr bgcolor="#9acd32">
                                <th align="left">Title</th>
                                <th align="left">Artist</th>
                            </tr>
                            <xsl:for-each select="catalog/cd">
                                <tr>
                                    <td><xsl:value-of select="title"/></td>
                                    <td><xsl:value-of select="artist"/></td>
                                </tr>
                            </xsl:for-each>
                        </table>
                    </body></html>
                </xsl:template>
        
                </xsl:stylesheet> 
            def xmlInput(self):
                <?xml version="1.0" encoding="ISO-8859-1"?>
                <catalog>
                    <cd>
                        <title>Empire Burlesque</title>
                        <artist>Bob Dylan</artist>
                    </cd>
                    <cd>
                        <title>Hide your heart</title>
                        <artist>Bonnie Tyler</artist>
                    </cd>
                </catalog>
        
            """

def initServer():
    genericStore.itemList=[bookStore, dvdStore, videoGameStore]

########################
CherryClass GenericStore:
########################
mask:
    def index(self):
        # Home page: display the list of item types and let the user choose one
        <html><body><center><br><br><br>
            Welcome to the store. Choose what you want to buy:<br><br>
            <table cellspacing=10><tr>
            <py-for="itemType in self.itemList">
                <td py-attr="itemType.color" bgcolor="">
                    <a py-attr="itemType.getPath()+'/viewList'" href="" py-eval="itemType.label+'s'"></a>
                </td>
            </py-for>
            </tr></table>
        </center></body></html>
    def viewList(self):
        <html><body><center><br><br><br>
        <b py-eval="self.label.upper()+'S'"></b><br><br>
        Click on a <py-eval="self.label"> title to view it:<br><br>
        <table py-attr="self.color" bgcolor="" cellpadding=5>
            <py-for="item in self.itemList">
                <tr><td><a py-attr="self.getPath()+'/viewItem?itemIndex=%s'%_index" href="" py-eval="item[0]"></a></td></tr>
            </py-for>
        </table>
        </center></body></html>
    # Default viewItem mask (used for DVDs and Video games). Will be overwritten for books
    def viewItem(self, itemIndex):
        <py-exec="title, price=self.itemList[int(itemIndex)]">
        <html><body><center><br><br><br>
            <table py-attr="self.color" bgcolor="" cellpadding=5>
                <tr><td>Title: <py-eval="title"></td></tr>
                <tr><td>Price: <py-eval="price">$</td></tr>
            </table>
        </center></body></html>
        
########################
CherryClass BookStore(GenericStore):
########################
variable:
    label='book'
    color='pink'
    itemList=[('Harry Potter and the Goblet of Fire', '18', 'J. K. Rowling'), ('I love CherryPy', '5', 'Remi Delon')]
mask:
    # We have to overwrite viewItem for books, because we have to display the author too
    def viewItem(self, itemIndex):
        <py-exec="title, price, author=self.itemList[int(itemIndex)]">
        <html><body><center><br><br><br>
            <table py-attr="self.color" bgcolor="" cellpadding=5>
                <tr><td>Title: <py-eval="title"></td></tr>
                <tr><td>Price: <py-eval="price">$</td></tr>
                <tr><td>Author: <py-eval="author"></td></tr>
            </table>
        </center></body></html>

########################
CherryClass DvdStore(GenericStore):
########################
variable:
    label='DVD'
    color='red'
    itemList=[('Star Wars Episode 1', '25'), ('The Legend of CherryPy', '4')]

########################
CherryClass VideoGameStore(GenericStore):
########################
variable:
    label='video game'
    color='yellow'
    itemList=[('Cool Rider 3', '29'), ('CherryPy Eating Contest', '7')]

#############
CherryClass HttpProtected(HttpAuthenticate):
#############
function:
    def getPasswordListForLogin(self, login):
        if login=="login": return ["password"]    
        return []
mask:
    def index(self):
        <html><body>You're in, your login is:<py-eval="self.login"></body></html>

#############
CherryClass CookieProtected(CookieAuthenticate):
#############
function:
    def getPasswordListForLogin(self, login):
        if login=="login": return ["password"]    
        return []
mask:
    def index(self):
        <html><body>
            You're in, your login is: <py-eval="self.login"><br>
            Click <a href="doLogout">here</a> to log out.
        </body></html>

#############
CherryClass TestForm(Form):
#############
function:
    def __init__(self):
        headerSep=FormSeparator('', defaultFormMask.defaultHeader)
        textField=FormField(label='Text field:', name='textField', mandatory=1, typ='text')
        textareaField=FormField(label='Textarea field:', name='textareaField', mandatory=1, typ='textarea', size='30x5')
        selectField=FormField(label='Select field:', name='selectField', mandatory=1, typ='select', optionList=['Option 1', 'Option 2', 'Option 3'])
        radioField=FormField(label='Radio field:', name='radioField', mandatory=1, typ='radio', optionList=['Option 1', 'Option 2', 'Option 3'])
        checkboxField=FormField(label='Checkbox field:', name='checkField', mandatory=0, typ='checkbox', optionList=['Option 1', 'Option 2', 'Option 3'])
        submitField=FormField(label='', name='Submit', typ='submit')
        footerSep=FormSeparator('', defaultFormMask.defaultFooter)

        self.fieldList=[headerSep, textField, textareaField, selectField, radioField, checkboxField, submitField, footerSep]

mask:
    def index(self, **kw):
        <html><body>
        <h2>Form handling:</h2><br>
        Handling forms can really be pain, especially if you want to handle user errors (missing field, incorrect values, ...).<br>
        CherryPy provides a <i>Form</i> standard module to make that task easier. The module is able to validate the
        fields, and to redisplay the form with some error messages if some fields were incorrect. You can also
        customize it to change the design of the form.<br>
        Below is a sample code that uses the form module:<br>
        <py-eval="demo.viewCode(demo.formCode())">
        <br>Result:<br><br>
            Fill out the form and hit "Submit". If you forget any mandatory fields, the form will
            be displayed again, and the errors will be indicated:<br>
            <py-eval="self.formView(0)">
        </body></html>

view:
    def postForm(self, **kw):
        if self.validateForm():
            res="<html><body>"
            for key, value in kw.items():
                res+="%s : %s <br>"%(key, value)
            return res+"</body></html>"
        else:
            return "<html><body><font color=red>Fill out missing fields</font>"+self.formView(1)+"</body></html>"


