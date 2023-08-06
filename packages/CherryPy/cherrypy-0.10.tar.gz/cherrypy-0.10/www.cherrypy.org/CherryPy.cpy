use FrenchTools, HttpAuthenticate, MaskTools, Mail, CherryPyForumDesign

import time, cPickle

def initAfterBind():
    # On the production machine, switch user to "cherrypy"
    if configFile.get('restrictedArea', 'login') != 'login':
        os.setegid(2524) 
        os.seteuid(2524)

def initRequest():
    if request.browserUrl.find('static')==-1 and request.browserUrl.find('viewStat')==-1 and request.browserUrl.find('maskTools')==-1:
        sql.logPageStat()

def onError():
    import traceback, StringIO
    bodyFile=StringIO.StringIO()
    traceback.print_exc(file=bodyFile)
    errorBody=bodyFile.getvalue()
    bodyFile.close()
    try: errorBody+="\nUrl was: "+request.browserUrl+"\n"
    except: pass
    if request.base.find('cherrypy.org')!=-1:
        if request.path.find('robots.txt')==-1:
            cherryPyMail.sendMail("erreur@cherrypy.org", "rdelon@netcourrier.com", "", "text/plain", "Erreur CherryPy", errorBody)
        response.body="<html><body><center><br><br><br>Oops, an internal error occured.<br><br>We've been notified of this and we'll try to fix it as soon as possible</body></html><!-- %s -->"%errorBody
    else:
        response.body=errorBody
        response.headerMap['content-type']='text/plain'

def initServer():
    sys.path.append("/home/rdelon/PythonModules")
    # Read keyWordMapFile (used for search function)
    keyWordMapFile=configFile.get("keyWordMap", "file")
    f=open(keyWordMapFile,"r")
    global keyWordMap
    keyWordMap=cPickle.load(f)
    f.close()

CherryClass CherryPyMail(Mail):
function:
    def __init__(self):
        self.smtpServer=configFile.get("mail","smtpServer")

CherryClass Root:
mask:
########################
#
# CONTENT TO UPDATE FREQUENTLY
#
########################
    def latestReleaseContent(self):
        <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.9.tar.gz?download">cherrypy-0.9.tar.gz</a> (1981K)
    def newsContent(self):
        <b>04/12 - Gmane interface to mailing list archives</b><br>
        Thanks to Hendrik Mans for pointing out that the CherryPy mailing archive is also available through Gmane. The web interface is at <a class=moduleLink href="http://news.gmane.org/gmane.comp.python.cherrypy">http://news.gmane.org/gmane.comp.python.cherrypy</a> and the NNTP interface is at nntp://news.gmane.org/gmane.comp.python.cherrypy.
        <br><br>
        <b>03/07 - CherryPy-0.10-rc1 released</b><br>
        There are many small improvements in this release. One of the main ones is that expired sessions are
        now automatically cleaned-up.<br>
        There are a couple of backward incompatibilities that affect custom sessions and the CookieSessionAuthenticate
        module.<br>
        You can download the release from the <a class=moduleLink py-attr="request.base+'/download'" href="">download area</a>
        <br><br>
        <b>02/22 - Wiki available</b><br>
        CherryPy now has a wiki where users can find extra informations and
        contribute their own content to share it with other people.<br>
        The wiki is available <a class=moduleLink href="http://wiki.cherrypy.org/cgi-bin/moin.cgi">here</a>.
        <br><br>
        <b>02/20 - New module in the bakery</b><br>
        Jeff Clement added a new module in the bakery: <b>jTime</b> is a multi-user web-based timesheet package.
        <br><br>
        <b>02/19 - Italian translation of the docs</b><br>
        Many thanks to Enrico Morelli who translated the tutorial and the HowTos into italian and put everything
        online on the italian Gentoo site: <a class=moduleLink href="http://www.gentoo.it">www.gentoo.it</a>
        <br><br>
        <b>01/20 - Nice little icon for the site :-)</b><br>
        As you will notice, the site now uses a nice little cherry as a favicon.ico
        <br><br>
        <b>01/18 - Bakery available</b><br>
        A new section called the "Bakery" has been added to this website. It will serve as a repository for
        third-party modules written CherryPy. Many thanks to Damien Boucard who developed this section.
        <br><br>
        <b>01/06 - CherryPy-0.10-beta released</b><br>
        The main change in this beta release is that you now have to use "request.sessionMap" instead of "sessionMap" in
        your code. This makes sessions completely thread-safe.<br>
        Another noticable change is that CherryPy now longer uses tabs: it uses 4 whitespaces everywhere instead.<br>
        This release also restores Jython compatibility, which had been broken in previous releases.<br>
        You can download the release from the <a class=moduleLink py-attr="request.base+'/download'" href="">download area</a>
        <br><br>
        <b>01/04 - Two new demos</b><br>
        There are two new entries in the <a class=moduleLink href="/demo/index">online demo</a>: a demo about SSL and a demo about streaming.
        <br><br>
        <b>12/15 - Improved Forum</b><br>
        A nasty bug that caused some messages in the Forum to sometimes get lost has been fixed.<br>
        Also, the ability to preview messages before you post them has been added.
        <br><br>
        <b>12/07 - Website update</b><br>
        The home page of this site has been changed to better explain what CherryPy is about and why it is good :-)<br>
        The left menu has also been reorganized and a couple of new sections have been added.<br><br>
        #<b>11/25 - CherryPy-0.9 released (at last :-)</b><br>
        #Just a few minor changes since the release candidate.<br>
        #This release is the first stable release in a looong time. The list of changes since the last stable release is huge so if you're still
        #using CherryPy-0.8, you are <b>strongly</b> encouraged to upgrade ...<br>
        #The ChangeLog can be found <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        #You can download this release from the <a class=moduleLink py-attr="request.base+'/download'" href="">download area</a>
        #<br><br>
        #<b>11/23 - Search system changed</b><br>
        #The search functionality on this website now uses Google to run searches ... (and since Google also indexes
        #the content of the forum, the search functionality of the forum has been removed)
        #<br><br>
        #<b>11/17 - CherryPy-0.9-rc1 released</b><br>
        #Many many improvements in this release candidate. The main one being an improved robustness for the HTTP server.
        #Check out the <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">ChangeLog</a> for a full
        #list of changes.<br>
        #I everything goes well, I hope to release 0.9-final early next week.<br>
        #You can download this release candidate from the <a class=moduleLink py-attr="request.base+'/download'" href="">download area</a>
        #<br><br>
        #<b>11/04 - CherryPy-0.9-final coming soon</b><br>
        #We're hard at work on the 0.9-final release. This release will have a loooong list of changes and improvements since
        #the previous release. Stay tuned ...<br><br>
        #<b>08/25 - CherryPy-0.9-gamma released</b><br>
        #The highlights of this release are: a new thread-pool server, sessions that work, the ability to store session
        #data in a database, plus many bugfixes...<br>
        #Check out <a class=moduleLink py-attr="request.base+'/cherrypy_0_9_gamma'" href="#">this page</a>
        #to find out a detailed list of what's new in this release, include the list of small backward
        #incompatibilities (that should only affect a small percentage of the sites using CherryPy).<br>
        #You can download it from the <a class=moduleLink py-attr="request.base+'/download'" href="">download area</a>
        #<br><br>
        #<b>07/10 - Slides and photo from EuroPython 2003</b><br>
        #I've put online the slides I used to give a CherryPy presentation at EuroPython. There is also a picture
        #of the presentation (thanks Kevin :-)). You can see them
        #<a class=moduleLink py-attr="request.base+'/europython2003'" href="#">here</a>
        #<br><br>
        #<b>06/20 - CherryPy at EuroPython</b><br>
        #Well, after a lot of hesitation for various reasons, I finally decided to go to
        #<a class=moduleLink href="http://www.europython.org">EuroPython 2003</a>. Unfortunately,
        #all talks were closed so I won't be able to make a talk about CherryPy. But I'll be able to make a lightning
        #talk. 5 minutes is not much to talk about CherryPy, but it's better than nothing ...
        #The talk will be given on Friday June 27th, sometime in the afternoon. I look forward to meeting everybody
        #there :-)
        #<br><br>
        #<b>06/19 - CherryPy-0.9-beta released</b><br>
        #This beta release includes many bugfixes, session handling, improved XML-RPC support...
        #It is compatible with python-2.3 and works with Jython. It also comes with a regression test suite.<br>
        #In fact, it has so many new features that we've put together a special page explaining what's new in this
        #release. Check out this page <a class=moduleLink py-attr="request.base+'/cherrypy_0_9_beta'" href="#">here</a>.<br>
        #Note that this release brings some backward incompatilities (that should only affect a small percentage of
        #the sites using CherryPy though).<br>
        #You can download it from the <a class=moduleLink py-attr="request.base+'/download'" href="">download area</a>
        #<br><br>
        #<b>06/13 - Forum available !</b><br>
        #Alright, here is the scoop: I've been working on a new framework that runs on top of CherryPy ...
        #This framework will
        #help you write web application that manipulate complicated data, with all kind of relationships among your data.<br>
        #The code name for this framework is "<b>CherryObjects</b>" ... Anyway, I'm hoping to release a first beta version
        #in a few weeks.<br>
        #In the mean time, I've written a first application that uses this framework: <b>a web forum</b> (judiciously
        #called "<a class=moduleLink py-attr="request.base+'/cherryForum'" href="">CherryForum</a>"). So I've put online
        #an instance of CherryForum that will be used as a forum for the CherryPy community as well as a demonstration
        #of CherryForum. The forum is available <a class=moduleLink py-attr="request.base+'/myForum/index'" href="">here</a>
        #<br><br>
        #<b>06/11 - New version on the way</b><br>
        #We're hard at work on the next release of CherryPy. This release will include many bugfixes, session handling,
        #improved XML-RPC support... It will be compatible with python-2.3 and will work with Jython. If we have time,
        #it will come with an extensive regression test suite. We hope to release it in 2 or 3 weeks ...
        #<br><br>
        #<b>04/16 - Debian package available</b><br>
        #Thanks to Raphael Goulais, CherryPy is now available as a Debian package
        #<a class=moduleLink href="http://packages.debian.org/unstable/web/cherrypy.html">here</a>.<br>
        #It is now in the "unstable" distribution, but it will move into "testing" soon and eventually into "stable".
        #<br><br>
        #<b>03/24 - New section on the website</b><br>
        #We've added a new section on the website called
        #<a class=moduleLink py-attr="request.base+'/talk'" href="">They talk about CherryPy</a> which includes articles and
        #quotes from CherryPy users, as well as links to these articles.
        #<br><br>
        #<b>02/20 - One more CherryPy hosting provider</b><br>
        #<a class=moduleLink href="http://www.python-hosting.com">Python-hosting.com</a> is a new hosting provider specialized in python.<br>
        #CherryPy is in the list of supported software.
        #<br><br>
        #<b>02/06 - New functionality on FreeCherryPy</b><br>
        #FreeCherryPy just became more flexible. You now have the ability to compile your source files (.cpy) on your local
        #machine and to upload the resulting .py file on FreeCherryPy.<br>
        #This gets rid of the annoying constraint of having
        #to use a single source file for your website.<br>
        #FreeCherryPy is available <a class=moduleLink href="http://www.freecherrypy.org">here</a>.
        #<br><br>
        #<b>01/27 - Documentation available in PostScript format</b><br>
        #Some people reported that they were unable to print the PDF files available in the documentation
        #section. To provide an alternative to these PDF files, we've added a PostScript version.
        #<br><br>
        #<b>01/13 - New search function on the website</b><br>
        #A "search" functionality is now available on this website. It allows you to search keywords on all pages of the
        #website and the documentation. The search box is on the top left corner of the screen, just underneath the nice logo :-)
        #<br><br>
        #<b>01/10 -</b> <a class=moduleLink py-attr="request.base+'/download'" href=""><b>CherryPy-0.8 released</b></a><br>
        #This release includes all the improvement from the beta release (mostly a brand new HTTP server) and it fixes a few bugs.
        #The documentation has also been updated.
        #<br><br>
        #<b>12/17 - New mailing list: cherrypy-devel </b><br>
        #A new mailing list called cherrypy-devel has been created. It is dedicated to the development of CherryPy itself.
        #Information is available from the <a class=moduleLink py-attr="request.base+'/mailingLists'" href="">mailing lists</a> section
        #<br><br>
        #<b>12/17 - CherryPy-0.8-beta released</b><br>
        #This release includes a new/more flexible/more robust HTTP server, XML-RPC support, hidden masks/views and
        #documentation about these new features.<br>
        #This is the first time we're making a beta release. The reason is that it includes major changed, and also that the
        #community is getting bigger so we can hope to get enough feedback before the 0.8 release.<br>
        #More information (including the download link) is available in the <a class=moduleLink py-attr="request.base+'/download'" href="">download area</a>
        #<br><br>
        #<b>11/17 - New article about CherryPy in the PythonJournal</b><br>
        #If you want to know the history of CherryPy, check out the article about it in the
        #<a class=moduleLink href="http://pythonjournal.cognizor.com">PythonJournal</a>
        #<br><br>
        #<b>10/30 - A "real" HTTP server on the way ...</b><br>
        #Thanks to Brian Meagher. Check out the <a class=moduleLink py-attr="request.base+'/currentDevelopment'" href="">current development</a> section for more information.
        #<br><br>
        #<b>10/03 - One more CherryPy hosting provider</b><br>
        #<a class=moduleLink href="http://hostandpost.cognizor.com">Cognizor's Host and Post</a> is now providing CherryPy hosting services.
        #<br><br>
        #<b>09/24 - One more HowTo</b><br>
        #One more HowTo has been added to the documentation: How to create a spinning server and then debug it.<br>
        #This is based on a true story :-)
        #<br><br>
        #<b>09/18 -</b> <a class=moduleLink py-attr="request.base+'/download'" href=""><b>CherryPy-0.7 Released (minor bugfixes)</b></a><br>
        #Minor bugs have been fixed and error reporting has been improved.<br>
        #The much awaited HowTo that explains how to use AOP (Aspect Oriented Programming) with CherryPy has been added
        #to the documentation.
        #<br><br>
        #<b>09/12 - XML/XSL HowTo and demo available</b><br>
        #It is very easy to use XML/XSL with CherryPy. A new HowTo has been added to the documentation to explain how to
        #do it (based on the 4Suite package).<br>
        #A new demo has also been added to demonstrate how this works. The demo also features a handy
        #<a class=moduleLink py-attr="request.base+'/demo/xmlXslOnline'" href="">online XML/XSL transformation tool</a> !
        #<br><br>
        #<b>09/02 -</b> <a class=moduleLink py-attr="request.base+'/download'" href=""><b>CherryPy-0.6 Released (feature improvement)</b></a><br>
        #This release adds SSL support (based on PyOpenSSL) to CherryPy. It also removes the GPL license from Httpd.py and from the
        #executable generated by CherryPy.
        #One HowTo has been added to the documentation to explain how to use SSL support.<br>
        #Many thanks to Mark Wormgoor for his contribution to the SSL code.
        #<br><br>
        #<b>08/25 -</b> <a class=moduleLink py-attr="request.base+'/license'" href=""><b>New license section on the web site</b></a><br>
        #As more and more users send us questions about CherryPy's licensing method, we've added a special
        #<a class=moduleLink py-attr="request.base+'/license'" href="">license</a> section on the web site to clarify
        #our position.
        #<br><br>
        #<b>08/08 -</b> <a class=moduleLink py-attr="request.base+'/download'" href=""><b>CherryPy-0.5 Released (feature improvement)</b></a><br>
        #This release adds FastCGI support as well as a new <py-eval="'&ltpy'+'-include&gt;'"> tag to include external templates
        #(to allow webdesigners to work on separate files).<br>
        #Two HowTos have been added to the documentation to explain how to use these new features.
        #<br><br>
        #<b>07/29 - One more HowTo</b><br>
        #Following the 0.4 release comes a new HowTo that explains how to use the new caching capability.
        #<br><br>
        #<b>07/29 -</b> <a class=moduleLink py-attr="request.base+'/download'" href=""><b>CherryPy-0.4 Released (feature improvement)</b></a><br>
        #This release adds caching capability, as well as some compiler optimization (thanks to Andreas Kostyrka).<br>
        #Note that this release brings a minor backward incompatibility (that should only affect very few programs).
        #<br><br>
        #<b>07/26 - Two more HowTos</b><br>
        #Two useful HowTos have been added to the documentation:<ul>
        #<li>How to compile your code in debug mode</li>
        #<li>How to use the hotReload feature of CherryPy</li>
        #</ul>
        #<b>07/25 -</b> <a class=moduleLink href="http://www.freecherrypy.org"><b>Free CherryPy hosting available</b></a><br>
        #FreeCherryPy is please to offer free CherryPy hosting services.
        #This offer is limited to non-commercial web sites.<br>
        #Check it out <a class=moduleLink href="http://www.freecherrypy.org">here</a>
        #<br><br>
        #<b>07/24 - One more HowTo</b><br>
        #One more HowTo has been added to the documentation:<br>
        #How to use load-balancing for your CherryPy web site
        #<br><br>
        #<b>07/19 - One more HowTo</b><br>
        #The HowTo that explains how to run CherryPy behind Apache has been updated, thanks to Andreas Kostyrka.<br>
        #The HowTo now explains several ways to do it:
        #<ul>
        #<li>Using persistent CGI</li>
        #<li>Using mod_rewrite (or mod_proxy), which is faster than persistent CGI</li>
        #</ul>
        #<b>07/17 -</b> <a class=moduleLink py-attr="request.base+'/download'" href=""><b>CherryPy-0.3 Released (documentation and demo improvement)</b></a><br>
        #This release includes a new demo entry (OOP) as well as some new documentation (Standard Library)
        #<br><br>
        #<b>07/17 - CherryPy Standard Library documentation available</b><br>
        #The documentation for the CherryPy Standard Library is finally available.
        #See the <a class=moduleLink py-attr="request.base+'/documentation'" href="">documentation</a> page.
        #<br><br>
        #<b>07/16 - One more demo</b><br>
        #We've added an entry in the demo. It is called "Using OOP to develop a web site".
        #Check it out <a class=moduleLink py-attr="request.base+'/demo/index'" href="">here</a>
        #<br><br>
        #<b>07/08 - One more HowTo</b><br>
        #One more HowTo has been added to the documentation:<br>
        #How to connect a CherryPy server to a database
        #<br><br>
        #<b>07/04 -</b> <a class=moduleLink py-attr="request.base+'/download'" href=""><b>CherryPy-0.2 Released (minor improvement)</b></a><br>
        #This release fixes a small bug that prevented non-Unix users from using the CookieAuthenticate module.
        #<br><br>
        #<b>07/03 - CVS repository available</b><br>
        #Thanks to sourceforge, CherryPy's source code is now available to everyone through
        #CVS. Check out the <a class=moduleLink py-attr="request.base+'/cvs'" href="">CVS page</a>
        #<br><br>
        #<b>07/03 - Two more HowTos</b><br>
        #Two useful HowTos have been added to the documentation:<ul>
        #<li>How to serve gzip-compress pages with CherryPy</li>
        #<li>How to run a CherryPy server behind Apache</li>
        #</ul>
        #<b>06/30 -</b> <a class=moduleLink py-attr="request.base+'/download'" href=""><b>CherryPy-0.1 Released (first public release)</b></a><br>
        #We're pleased to announce the first public release of CherryPy. Even though the
        #release number is low (0.1), CherryPy has already been used in production for 6 months
        #and has proven fast and stable.

    def downloadContent(self):
        <b>Latest non-stable release: CherryPy-0.10-rc1</b><br>
        There are many small improvements in this release. One of the main ones is that expired sessions are
        now automatically cleaned-up.<br>
        There are a couple of backward incompatibilities that affect custom sessions and the CookieSessionAuthenticate
        module:<br>
        "isGoodLoginAndPassword" has been replaced with "checkLoginAndPassword" and can now return several error
        messages (or None if everything is OK).<br>
        The login is no longer stored in "self.login" but in "request.login" for thread-safety.<br>
        Check out the HowTo about sessions (from the documentation that comes with the release) to learn how the new custom
        sessions work and how expired sessions are cleaned up.<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.10-rc1.tar.gz?download">cherrypy-0.10-rc1.tar.gz</a> (2133 KB) (courtesy of sourceforge)<br>
        The detailed ChangeLog can be viewed
        <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older non-stable release: CherryPy-0.10-beta</b><br>
        The main change in this beta release is that you now have to use "request.sessionMap" instead
        of "sessionMap" in your code. This makes sessions completely thread-safe.<br>
        Another noticable change is that CherryPy now longer uses tabs: it uses 4 whitespaces everywhere instead.<br>
        This release also restores Jython compatibility, which had been broken in previous releases.<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.10-beta.tar.gz?download">cherrypy-0.10-beta.tar.gz</a> (2001 KB) (courtesy of sourceforge)<br>
        The detailed ChangeLog can be viewed
        <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Latest stable release: CherryPy-0.9</b><br>
        This is the first stable release in a long time and the list of changes since the last stable release is huge. So if you're still using
        CherryPy-0.8, you're <b>strongly</b> encouraged to upgrade ...<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.9.tar.gz?download">cherrypy-0.9.tar.gz</a> (1981 KB) (courtesy of sourceforge)<br>
        The ChangeLog can be viewed <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older non-stable release: CherryPy-0.9-rc1</b><br>
        Many many improvements in this release.
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.9-rc1.tar.gz?download">cherrypy-0.9-rc1.tar.gz</a> (1996 KB) (courtesy of sourceforge)<br>
        The ChangeLog can be viewed <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older non-stable release: CherryPy-0.9-gamma</b><br>
        The highlights of this release are: a new thread-pool server, sessions that work and many bugfixes.<br>
        We've put together a page explaining what's new
        in this release <a class=moduleLink py-attr="request.base+'/cherrypy_0_9_gamma'" href="#">here</a>.<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.9-gamma.tar.gz?download">cherrypy-0.9-gamma.tar.gz</a> (1903K) (courtesy of sourceforge)<br>
        <br>
        <b>Older non-stable release: CherryPy-0.9-beta</b><br>
        This release includes a lot of improvements and new features. We've put together a page explaining what's new
        in this release <a class=moduleLink py-attr="request.base+'/cherrypy_0_9_beta'" href="#">here</a>.<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.9-beta.tar.gz?download">cherrypy-0.9-beta.tar.gz</a> (1931K) (courtesy of sourceforge)<br>
        <br>
        <b>Older stable release: CherryPy-0.8</b><br>
        This release includes all the improvements from the 0.8-beta release and it fixes a few bugs. It also adds a new way
        to control CherryPy logging. A HowTo has been added to the documentation about that.<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.8.tar.gz?download">cherrypy-0.8.tar.gz</a> (1359K) (courtesy of sourceforge)<br>
        The ChangeLog can be viewed <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older release: CherryPy-0.8-beta</b><br>
        Lots of changes in this release:
        <ul>
        <li>First of all, a brand new HTTP server: it is based on BaseHTTPServer, but it has been heavily
        customized to support AF_UNIX sockets and SSL. The new server supports threading and forking. It doesn't support
        asyncore service yet (maybe in the next release). A new chapter called "Deploying your website for production"
        has been added to the tutorial and it explains how to use these new features.</li>
        <li>XML-RPC support: CherryPy is the perfect tool to develop XML-RPC services.
        A new HowTo in the documentation explains how to develop an XML-RPC server with CherryPy.</li>
        <li>Hidden views and masks: A new HowTo in the documentation explains what this is</li>
        </ul>
        <b>The new documentation is not available on the website yet. It is included when you download the beta release</b><br>
        This is the first time we're making a beta release. The reason is that it has lots of major changes (especially
        the HTTP server) and the community is getting big enough so we can hope to get some feedback. So please play with
        this release and let us know if you find any bugs.<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.8-beta.tar.gz?download">cherrypy-0.8-beta.tar.gz</a> (1369K) (courtesy of sourceforge)<br>
#        The ChangeLog can be viewed <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older release: CherryPy-0.7</b><br>
        Minor bugs have been fixed and error reporting has been improved.<br>
        The much awaited HowTo that explains how to use AOP (Aspect Oriented Programming) with CherryPy has been added
        to the documentation (note that the examples in the HowTo will only work with CherryPy-0.7 or later).<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.7.tar.gz?download">cherrypy-0.7.tar.gz</a> (1200K) (courtesy of sourceforge)<br>
        The ChangeLog can be viewed <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older release: CherryPy-0.6</b><br>
        This release adds SSL support to CherryPy.<br>
        One HowTo has been added to the documentation to explain how to use SSL.<br>
        This release also removes the copyright and the GPL license from Httpd.py and from the executable generated by CherryPy.<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.6.tar.gz?download">cherrypy-0.6.tar.gz</a> (1200K) (courtesy of sourceforge)<br>
        The ChangeLog can be viewed <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older release: CherryPy-0.5</b><br>
        This release adds FastCGI support as well as a new <py-eval="'&ltpy'+'-include&gt;'"> tag to include external templates
        (to allow webdesigners to work on separate files).<br>
        Two HowTos have been added to the documentation to explain how to use these new features.<br>
        It also improves the way filename extensions are recognized when serving static content.
        The content-type is now correctly set for most common extensions.<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.5.tar.gz?download">cherrypy-0.5.tar.gz</a> (1200K) (courtesy of sourceforge)<br>
        The ChangeLog can be viewed <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older release: CherryPy-0.4</b><br>
        This release adds a new caching capability to CherryPy.<br>
        It also includes some compiler optimization, which brings a minor backward incompatibility:<br>
        When you want to append some data to the <i>_page</i> variable in a mask, you now have to use: <i>_page.append("text")</i>
        instead of <i>_page+="text"</i>.<br>
        A new HowTo has been added to the documentation to explain how to use the caching capability.<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.4.tar.gz?download">cherrypy-0.4.tar.gz</a> (1200K) (courtesy of sourceforge)<br>
        The ChangeLog can be viewed <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older release: CherryPy-0.3</b><br>
        This release includes a new demo entry (OOP) as well as some new documentation (Standard Library)<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.3.tar.gz?download">cherrypy-0.3.tar.gz</a> (992K) (courtesy of sourceforge)<br>
        The ChangeLog can be viewed <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older release: CherryPy-0.2</b><br>
        This release fixes a small bug that prevented non-Unix users from using the CookieAuthenticate module. Other
        minor improvements have been made.<br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.2.tar.gz?download">cherrypy-0.2.tar.gz</a> (618K) (courtesy of sourceforge)<br>
        The ChangeLog can be viewed <a class=moduleLink py-attr="request.base+'/static/ChangeLog.txt'" href="">here</a><br>
        <br>
        <b>Older release: CherryPy-0.1</b><br>
        We're pleased to announce the first public release of CherryPy. Even though the
        release number is low (0.1), CherryPy has already been used in production for 6 months
        and has proven fast and stable.<br>
        The release comes with the documentation and a demo web site<br><br>
        Get the release here: <a class=moduleLink href="http://prdownloads.sourceforge.net/cherrypy/cherrypy-0.1.tar.gz?download">cherrypy-0.1.tar.gz</a> (354K) (courtesy of sourceforge)
########################
#
# CONTENT THATS SHOULD STAY THE SAME OFTEN
#
########################
    def square(self, title, body):
        <table border=0 cellspacing=0 cellpadding=0 width=100%>
            <tr>
                <td width=10><img py-attr="request.base+'/static/moduleHeaderLeft.gif'" src="" width=10 height=25></td>
                <td py-attr="request.base+'/static/moduleHeaderMiddle.gif'" background="" height=25 valign=top align=left class=moduleTitle py-eval="title"></td>
                <td width=10><img py-attr="request.base+'/static/moduleHeaderRight.gif'" src="" width=10 height=25></td>
            </tr><tr>
                <td width=10 py-attr="request.base+'/static/moduleBodyLeft.gif'" background="">&nbsp;</td>
                <td class=moduleText py-eval="body"></td>
                <td width=10 py-attr="request.base+'/static/moduleBodyRight.gif'" background="">&nbsp;</td>
            </tr><tr>
                <td width=10><img py-attr="request.base+'/static/moduleFooterLeft.gif'" src="" width=10 height=15></td>
                <td py-attr="request.base+'/static/moduleFooterMiddle.gif'" background="" height=15 py-eval="maskTools.x()"></td>
                <td width=10><img py-attr="request.base+'/static/moduleFooterRight.gif'" src="" width=10 height=15></td>
            </tr>
        </table>

    def leftSquare(self, title, body):
        <table border=0 cellspacing=0 cellpadding=5 width=100%>
            <tr><td align=left bgColor=#BD1E26 class=moduleTitle py-eval="title"></td></tr>
            <tr><td align=left class=moduleText py-eval="body"></td></tr>
        </table>
    
    def header(self, title, robots='all'):
        <html>
        <head>
            <meta name="robots" py-attr="robots" content="">
            <title>CherryPy : <py-eval="title"></title>
            <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
            <style type="text/css"> 
            <!--
            .moduleTitle {font-size:14px; font-weight:bold; color:white; font-family:arial}
            .moduleLink {font-size:12px; color:#BD1E26; font-family:arial} 
            .moduleLink:hover {font-size:12px; color:red; font-family:arial} 
            .moduleLinkB {font-size:12px; font-weight:bold; color:#BD1E26; font-family:arial} 
            .moduleLinkB:hover {font-size:12px; font-weight:bold; color:red; font-family:arial} 
            .moduleText {font-size:12px; color:black; font-family:arial}
            .moduleTextB {font-size:12px; font-weight:bold; color:#BD1E26; font-family:arial}
            --> 
            </style>
        </head>
        <body bgcolor=white topmargin="0" marginheight="0">
            <table width=100% cellspacing=20><tr>
                <td width=20% valign=top align=center class=moduleText>
                    <a py-attr="request.base" href=""><img py-attr="request.base+'/static/cherryPyLogo.gif'" src="" width=200 height=82 border=0 alt="CherryPy: A tasty toolkit for pythonic web development"></a><br>
                    <span style="font-size:5px;"><br></span>
                    <form target="_new" action="http://www.google.com/search" method="get" style="margin-top: 0; margin-bottom: 0" name="searchForm">
                        <b>Search:</b> <input type=text name=as_q size=10>&nbsp;&nbsp;
                        <input type=hidden name="as_sitesearch" value="cherrypy.org">
                        <input type=submit value=OK>
                    </form>
                    <span style="font-size:5px;"><br></span>
                    <table border=0 cellspacing=0 cellpadding=0 width=100%><tr><td bgColor=#FFCCCC>
                        <py-eval="self.leftColumn()">
                        #<br>
                        #<py-eval="self.leftSquare('Hosting services', self.hostContent())">
                        <br>
                        <py-eval="self.leftSquare('Latest stable release', self.latestReleaseContent())">
                    </td></tr></table>
                    <br>
                    <a href="http://sourceforge.net"><img py-attr="request.base+'/static/sourceForgeLogo.gif'" src="" width="88" height="31" border="0" alt="Many thanks to SourceForge"></a><br>
                    <br>
                    <a href="http://www.python.org"><img py-attr="request.base+'/static/PythonPoweredSmall.gif'" src="" border=0 alt="Powered by Python"></a><br>
                    <br>
                    <a href="http://www.cherrypy.org"><img py-attr="request.base+'/static/poweredByCherryPy.gif'" src="" border=0 alt="Powered by CherryPy"></a><br>
                </td>
    def footer(self):
            </tr></table>
            <center><small><small><font color=gray>
                Copyright &copy; 2002-2004 by Remi Delon. All Rights Reserved.<br>
                Comments and questions to <font color=gray>"remi at cherrypy.org"</font>
            </font></small></small></center>
        </body>
        </html>
    def index(self):
        <py-eval="self.header('A tasty toolkit for pythonic web development')">
            <td width=40% valign=top align=center>
                <py-eval="self.square('What is CherryPy ?', self.welcome())">
                <br>
                <py-eval="self.square('Compiler approach', self.compiler())">
                <br>
                <py-eval="self.square('Main features', self.mainFeatures())">
                #<br>
                #<py-eval="self.square('Let us know what you think', self.feedback())">
            </td>
            <td width=40% valign=top>
                <py-eval="self.square('News', self.newsContent())">
            </td>
        <py-eval="self.footer()">
    def hostContent(self):
        Looking for a place to host your CherryPy web site ?<br>
        Below is a list of "CherryPy-friendly" hosting service providers:<br><br>
        <a class=moduleLink href="http://www.freecherrypy.org"><b>FreeCherryPy</b></a> (<b>FREE, non commercial only)</b><br>
        <a class=moduleLink href="http://www.python-hosting.com">Python-hosting.com</a> (specialized python hosting)<br>
        <a class=moduleLink href="http://www.hurrah.com">Hurrah</a><br>
        <a class=moduleLink href="http://hostandpost.cognizor.com">Cognizor's Host and Post</a><br>
        <br>
        <a class=moduleLink py-attr="request.base+'/hosting'" href=""><small>Your name here</small></a>
    def feedback(self):
        We love receiving e-mails from users.<br>
        You like CherryPy ? You hate it ?<br>
        You're doing something cool with it ?<br>
        Let us know about it !<br>
        You can reach us at "remi at cherrypy.org".

    def showMe(self):
        CherryPy can do everything other famous application servers can do. But by using CherryPy and Python's power
        you might be able to save a lot of time and lines of code.<br><br>
        CherryPy was used to develop a major commercial web site called Urbishop.com (the website is no longer on-line).
        We wrote a first version of the web site with a "famous" application server, but we got a little frustrated with it.
        So we decided to rewrite everything with CherryPy. The result was much smaller code, developed in less time. And
        most importantly, we had FUN doing it !<br><br>
        Since then, we've used it to develop many other web sites, and the more we use it, the more we love it !<br><br>
        We've also put together a small demo that demonstrates a few of CherryPy capabilities. Check it out
        <a class=moduleLink py-attr="request.base+'/demo/index'" href="">here</a>
    def welcome(self):
        CherryPy is a Python based web development toolkit. It provides all the features of an enterprise-class application server while remaining
        light, fast and easy to learn.<br><br>
        CherryPy allows developers to build web applications in much the same way they would build any other object-oriented Python program. This usually results in smaller source code developed in less time.<br><br>
        It runs on most platforms (everywhere Python runs) and it is available under the <a class=moduleLink py-attr="request.base+'/license'" href="">GPL license</a>.<br><br>
        CherryPy is now nearly two years old and it is has proven very fast and stable. It is being used in production by many sites, from the simplest ones to the most demanding ones.<br><br>
        Oh, and most importantly: CherryPy is <b>fun</b> to work with :-)<br>

    def compiler(self):
        One of the main characteristics of CherryPy is that it works like a compiler:<br>
        You write source files, compile them with CherryPy and
        CherryPy generates an executable containing everything to run the web site (including an HTTP server).<br><br>
        This results in a very fast website that can be easily deployed (just by copying one file), either on its own or
        behind another webserver like Apache.<br>
        The built-in HTTP server is fast and robust. It supports SSL, XML-RPC and it can be deployed in many different
        ways: threading, forking, thread-pooling or process-pooling.

    def mainFeatures(self):
        Here are some the main features of CherryPy:
        <ul>
        <li>Encourages you to think of your website in an object-oriented way</li>
        <li>Supports some <a class=moduleLink href="/static/html/howto/node12.html">AOP</a> concepts as well</li>
        <li>Comes with a templating language but you can use other ones (like Cheetah) or use XML/XSL to generate your pages</li>
        <li>Can be easily connected to most databases</li>
        <li>Provides sessions out of the box (session data can be saved to RAM, disk, database, ...)</li>
        <li>Supports streaming in both directions</li>
        <li>Has a built-in cacheing mechanism</li>
        <li>Comes with a convenient standard library for things like Forms or Authentication</li>
        <li>All these features (especially sessions, database connections, cacheing, ...) work just as well in a threading or thread-pooling environment for production websites</li>
        </ul>

    def download(self):
        <py-eval="self.header('Download')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('Download', self.downloadContent())">
            </td>
        <py-eval="self.footer()">
    def people(self):
        <py-eval="self.header('People behind CherryPy')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('People behind CherryPy', self.peopleContent())">
            </td>
        <py-eval="self.footer()">
    def peopleContent(self):
        CherryPy was originally written by Remi Delon back in May 2002.<br><br>
        Since then, many people have helped and contributed to CherryPy one way or another.<br><br>
        Currently, the following people have write access to the CVS tree: Chema Cortes, Damien Boucard,
        Jeffrey Clement, Raphael Goulais, Steven Nieker and Ulf Bartelt.<br><br>
        The following people have also helped CherryPy one way or another: Brian Meagher, Bruce McTigue, Chris Foote,
        Cristian Echeverria, Darryl Caldwell, Enrico Morelli, Eric S. Johansson, Frederic Faure, John Cherry,
        John Platten, Kevin Manley, Lukasz Pankowski, Magnus Lycka, Mario Ruggier, Philippe Bouige,
        Salvatore Didio, Scott Luck, Tim Jarman.<br><br>
        A big thanks to everybody !

    def hosting(self):
        <py-eval="self.header('CherryPy hosting providers')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('CherryPy hosting providers', self.hostingContent())">
            </td>
        <py-eval="self.footer()">
    def hostingContent(self):
        Looking for a place to host your CherryPy site ?<br>
        Here is a list of CherryPy-friendly hosting providers:<br>
        <ul>
        <li><a class=moduleLink href="http://www.freecherrypy.org">FreeCherryPy.org</a>: Free CherryPy hosting (non commercial sites only and no database available)<br><br></li>
        <li><a class=moduleLink href="http://www.python-hosting.com">Python-Hosting.com</a>: Hosting provider specialized in Python<br><br></li>
        <li><a class=moduleLink href="http://www.hurrah.com">Hurrah.com</a><br><br></li>
        <li><a class=moduleLink href="http://hostandpost.cognizor.com/">Cognizor's Host and Post</a><br><br></li>
        </ul>
    #def about(self):
    #    <py-eval="self.header('About')">
    #        <td width=80% valign=top align=center>
    #            <py-eval="self.square('About', self.aboutContent())">
    #        </td>
    #    <py-eval="self.footer()">
    #def aboutContent(self):
    #    CherryPy is a Python-based tool for developing dynamic web sites. It uses many powerful concepts together, which makes
    #    it <b>unique</b> in its approach to web site development. It is available under the <a class=moduleLink py-attr="request.base+'/license'" href="">GPL license</a>.<br><br>
    #    Key properties/features of CherryPy are:
    #    <ul>
    #    <li>Based exclusively on Python (runs everywhere Python runs)</li>
    #    <li>Sits between a compiler and an application server</li>
    #    <li>Delivers fast, robust, and scalable web sites</li>
    #    <li>Developers can use OOP as well as <a class=moduleLink href="http://aosd.net">AOP (Aspect Oriented Programming)</a> concepts to develop web sites</li>
    #    <li>True separation of content and presentation</li>
    #    <li>Simple but powerful templating language</li>
    #    <li>"HTML editor safe" templating language (templates can go back and forth between designers and developers)</li>
    #    <li>Powerful standard libraries to make your life easy</li>
    #    </ul>
    #    Other properties/features are:
    #    <ul>
    #    <li>Can be linked to many databases (Oracle, Sybase, MySql, PostgreSql, ...)</li>
    #    <li>Can run behind another webserver (Apache, ...)</li>
    #    <li>Built-in sessions (session data can be saved in RAM, to a database, to disk, ...)</li>
    #    <li>Easy clustering and load-balancing set up for high-traffic web sites</li>
    #    <li>Built-in caching capability</li>
    #    <li>SSL support (based on PyOpenSSL)</li>
    #    <li>XML/XSL support (based on 4Suite)</li>
    #    <li>Built-in XML-RPC support</li>
    #    </ul>
    #    To learn more about the concepts and the story behind CherryPy, check out the
    #    <a class=moduleLink href="http://pythonjournal.cognizor.com/pyj3.1/cherrypy/CherryPy2.html">article</a> about
    #    it in the PythonJournal. (note that chapter 3 "Deploying with CherryPy" is deprecated because CherryPy's HTTP
    #    server now supports threading, forking, process pooling, ...)<br><br>
    #    <b>"Less code, more power"</b>
    def license(self):
        <py-eval="self.header('License')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('License', self.licenseContent())">
            </td>
        <py-eval="self.footer()">
    def licenseContent(self):
        <ul>
        <li><b>License</b><br>
        CherryPy is released under the <b>GPL license</b>.<br>
        However, since CherryPy works like a compiler and copies parts of itself into the generated script, the license includes a special clause that
        specifies that the GPL license doesn't apply to the code that's being copied into the executable.<br>
        Therefore, the websites generated by CherryPy are not affected by the GPL license.<br><br></li>
        <li><b>Copyright</b><br>
        Since the CherryPy-0.9 release, the copyright is owned by the "CherryPy Team" (see the file "CherryPyTeam.txt" included in each
        release for the list of people who make up this team).</li>
        </ul>
    def mailingLists(self):
        <py-eval="self.header('Mailing lists')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('Mailing lists', self.mailingListsContent())">
            </td>
        <py-eval="self.footer()">
    def mailingListsContent(self):
        CherryPy has three mailing lists hosted by sourceforge:
        <ul>
        <li><b>cherrypy-users</b> is the general list for all questions regarding the use of CherryPy.
            The list can be found <a class=moduleLink href="http://lists.sourceforge.net/lists/listinfo/cherrypy-users">here</a><br><br></li>
        <li><b>cherrypy-devel</b> is the list dedicated to the development (new features, bug fixes, design choices, ...) of CherryPy itself.
            The list can be found <a class=moduleLink href="http://lists.sourceforge.net/lists/listinfo/cherrypy-devel">here</a><br><br></li>
        <li><b>cherrypy-announce</b> is a very low-traffic list where all new releases and major events are announced.
            You don't need to subscribe to this list if you've subscribed to cherrypy-users or cherrypy-devel.
            The list can be found <a class=moduleLink href="http://lists.sourceforge.net/lists/listinfo/cherrypy-announce">here<br><br></a></li>
        </ul>
        Note that the CherryPy mailing archive is also available through Gmane. The web interface is at <a class=moduleLink href="http://news.gmane.org/gmane.comp.python.cherrypy">http://news.gmane.org/gmane.comp.python.cherrypy</a> and the NNTP interface is at nntp://news.gmane.org/gmane.comp.python.cherrypy.
    def articles(self):
        <py-eval="self.header('Articles about CherryPy')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('Articles about CherryPy', self.articlesContent())">
            </td>
        <py-eval="self.footer()">
    def articlesContent(self):
        Here is a list of articles/presentations that have been written about CherryPy:
        <ul>
        <li>
            <b>Web development with CherryPy</b> by Jeffrey Clement, August 2003.<br>
            Very good slides from a presentation given by Jeffrey Clement to the Calgary Linux Users Group.<br>
            Available in <a class=moduleLink href="/static/cherrypy-clug.pdf">PDF format</a> and
            <a class=moduleLink href="/static/cherrypy-clug-handout.pdf">PDF handout format</a><br><br>
        </li>
        <li>
            <b>Introduction to CherryPy</b> by Remi Delon, June 2003.<br>
            Slides from a small presentation given by Remi Delon at Europython 2003.<br>
            Available in <a class=moduleLink href="/static/CherryPy-EuroPython2003.pdf">PDF format</a> and
            <a class=moduleLink href="/static/CherryPy-EuroPython2003.ppt">PowerPoint format</a><br>
            As a bonus, a photo of the talk is available <a class=moduleLink href="/static/Cherrypy-EuroPython.jpg">here</a> :-)<br><br>
        </li>
        <li>
            <b>Smart Websites with CherryPy</b> by Remi Delon, November 2002.<br>
            Article written by Remi Delon for the PythonJournal. Explains the background of CherryPy and the concepts
            behind it. The last paragraph about deployment is outdated because the HTTP server is now much better.<br>
            The article is available
            <a class=moduleLink href="http://pythonjournal.cognizor.com/pyj3.1/cherrypy/CherryPy2.html">here</a><br><br>
        </li>
        </ul>

    def downloadableDoc(self):
        <py-eval="self.header('Downloadable/printable docs')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('Downloadable/printable docs', self.downloadableDocContent())">
            </td>
        <py-eval="self.footer()">
    def downloadableDocContent(self):
        The tutorial is available in <a class=moduleLink py-attr="request.base+'/static/pdf/tut.pdf'" href="">PDF format</a> (124K)
        and in <a class=moduleLink py-attr="request.base+'/static/pdf/tut.ps'" href="">Postscript format</a> (129K).<br><br>
        The HowTos are available in <a class=moduleLink py-attr="request.base+'/static/pdf/howto.pdf'" href="">PDF format</a> (98K)
        and in <a class=moduleLink py-attr="request.base+'/static/pdf/howto.ps'" href="">Postscript format</a> (100K).<br><br>
        The standard library documentation is available in <a class=moduleLink py-attr="request.base+'/static/pdf/lib.pdf'" href="">PDF format</a> (47K)
        and in <a class=moduleLink py-attr="request.base+'/static/pdf/lib.ps'" href="">Postscript format</a> (59K).<br><br>
        All of these (plus the HTML format) are included when you download CherryPy.

    def cvs(self):
        <py-eval="self.header('CVS')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('CVS', self.cvsContent())">
            </td>
        <py-eval="self.footer()">
    def cvsContent(self):
        CherryPy has a CVS repository hosted by sourceforge.<br>
        You can check out the modules through anonymous (pserver) CVS. Just use the following commands:<br>
        <br>
        cvs -d:pserver:anonymous@cvs.cherrypy.sourceforge.net:/cvsroot/cherrypy login<br>
        cvs -z3 -d:pserver:anonymous@cvs.cherrypy.sourceforge.net:/cvsroot/cherrypy co cherrypy<br>
        <br>
        Simply press enter when prompted for a password.<br><br>
        #(you might also have to set the CVS_RSH environment variable to "ssh", using a command like "export CVS_RSH='ssh'").<br><br>
        The CVS repository can also be viewed online <a class=moduleLink href="http://cvs.sourceforge.net/cgi-bin/viewcvs.cgi/cherrypy/">here</a>
    def documentation(self):
        <py-eval="self.header('Documentation')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('Introduction', self.introductionContent())">
                <br>
                <py-eval="self.square('Tutorial', self.tutorialContent())">
                <br>
                <py-eval="self.square('HowTo', self.howToContent())">
                <br>
                <py-eval="self.square('CherryPy Standard Library', self.libContent())">
                <br>
                <py-eval="self.square('Mailing lists', self.mailingListsContent())">
                #<br>
                #<py-eval="self.square('Coming soon...', self.comingSoonContent())">
            </td>
        <py-eval="self.footer()">
    def introductionContent(self):
        To learn more about the concepts and the story behind CherryPy, check out the
        <a class=moduleLink href="http://pythonjournal.cognizor.com/pyj3.1/cherrypy/CherryPy2.html">article</a> about
        it in the PythonJournal. (note that chapter 3 "Deploying with CherryPy" is deprecated because CherryPy's HTTP
        server now supports threading, forking, process pooling, ...)
    def tutorialContent(self):
        The best way to learn about CherryPy is to follow the tutorial.<br>
        You can browse it online <a class=moduleLink py-attr="request.base+'/static/html/tut/index.html'" href="">here</a>.<br>
        It is also available in pdf format <a class=moduleLink py-attr="request.base+'/static/pdf/tut.pdf'" href="">here</a> (124K)
        and in postscript format <a class=moduleLink py-attr="request.base+'/static/pdf/tut.ps'" href="">here</a> (129K).
    def howToContent(self):
        For a more advanced use of CherryPy, check out the HowTo list.<br>
        You can browse it online <a class=moduleLink py-attr="request.base+'/static/html/howto/index.html'" href="">here</a>.<br>
        It is also available in pdf format <a class=moduleLink py-attr="request.base+'/static/pdf/howto.pdf'" href="">here</a> (98K)
        and in postscript format <a class=moduleLink py-attr="request.base+'/static/pdf/howto.ps'" href="">here</a> (100K).
        
    def libContent(self):
        CherryPy comes with a set of useful CherryClasses. These CherryClasses make the CherryPy Standard Library.<br>
        You can browse the documentation online <a class=moduleLink py-attr="request.base+'/static/html/lib/index.html'" href="">here</a>.<br>
        It is also available in pdf format <a class=moduleLink py-attr="request.base+'/static/pdf/lib.pdf'" href="">here</a> (47K)
        and in postscript format <a class=moduleLink py-attr="request.base+'/static/pdf/lib.ps'" href="">here</a> (59K).
    def comingSoonContent(self):
        - CHTL and CGTL reference<br>
        - CherryPy source files syntax reference<br>
        - More HowTo's<br>
        - FAQ<br>
        - ...
    def currentDevelopment(self):
        <py-eval="self.header('Current development')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('Current development', self.currentDevelopmentContent())">
            </td>
        <py-eval="self.footer()">
    def currentDevelopmentContent(self):
        Here are the things we're working on at the moment:
        <ul>
        #<li>
        #    <b>High priority</b>:
        #    <ul>
        #    <li>A search function on the website (to be able to search the documentation)</li>
        #    </ul>
        #    <br>
        #</li>
        <li>
            <b>Low priority</b>:
            <ul>
            <li><b>SSL demo</b>: CherryPy already supports SSL, so we're working on putting together a demo to prove it :-)</li>
            <li><b>More HowTos</b>: The tutorial is a good starting point for learning to develop a website, but we're working on
            writing more HowTos that will explain how to do more advanced things...</li>
            </lu>
        </li>
        </ul>

    def aboutSite(self):
        <py-eval="self.header('About CherryPy.org')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('About CherryPy.org', self.aboutSiteContent())">
            </td>
        <py-eval="self.footer()">
    def aboutSiteContent(self):
        This site itself is a nice example of a setup that can be used for most production websites.<br>
        There is a HowTo that describes exactly how this site is set up. It can be found
        <a class=moduleLink href="/static/html/howto/node22.html">here</a>.<br><br>
        In short:
        <ul>
        <li>The site runs on Python-2.3 and it uses the latest CherryPy version</li>
        <li>The HTTP server runs a pool of threads and it runs exposed (no Apache)</li>
        <li>Each thread has its own connection to a MySql database</li>
        <li>The site uses sessions. Session data is stored in RAM and all threads have access to it (so it doesn't matter if two requests from the same client are handled by two different threads)</li>
        <li><b>The site runs for weeks without having to be restarted or leaking memory</b></li>
        </ul>

    def talk(self):
        <py-eval="self.header('They talk about CherryPy')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('They talk about CherryPy', self.talkContent())">
            </td>
        <py-eval="self.footer()">
    def talkContent(self):
        Here is what users say about CherryPy:<br><br>
        #<i>
        #"Remi, I'm fascinated with CherryPy. It's the best web tool I've seen..."
        #</i><br>
        #<a class=moduleLink href="http://www.cherrypy.org/myForum/viewThread?threadId=40">David on Dec 2, 2003</a>
        #<br><br>
        <i>
        "Just wanted to give another huge thank you for a wonderful tool.  I built a
        auction catalog service for a client using CherryPy 0.9 and it handled like
        a charm.  The site was basically a large searchable catalog and coincides with
        a satellite TV auction (meaning that everyone is hitting the server all at once
        as a new lot comes up).  During the sale the site was easily 5 or 10 requests
        per second and it barely made a blip on the server it was running on.  My setup
        was two separate instances of CP running in ThreadPool mode behind balance
        behind Apache.  I wanted a couple separate servers in case one died but neither
        of them did.  Everything worked flawlessly and the client was very happy.
        <br>
        A year before I had built a version using webware and it brought the server
        down under the load.  I decided to move to CP because it was easier and simpler
        to follow what was happening.  I'm really happy with it."
        </i><br>
        <a class=moduleLink href="http://sourceforge.net/mailarchive/forum.php?thread_id=3547475&forum_id=9986">Jeff Clement on Dec 1, 2003</a>
        <br><br>
        <i>
        "CherryPy is such an intuitive way to produce dynamic web pages. Remi has
        provided a first rate package that does everything I need. The excellent
        documentation makes it easy to learn CherryPy. The templating languages,
        standard libraries and examples are great building blocks that allow a
        relative Python newbie like me to create a very functional Intranet site."
        </i><br>
        <a class=moduleLink href="http://sourceforge.net/mailarchive/forum.php?thread_id=2603446&forum_id=9986">Scott Luck on Jun 17, 2003</a>
        <br><br>
        <i>
        "I am a ex-zope user and I love cherrypy. [...]
        CherryPy not only lets me develop in python, but bypasses zope's
        problem with regular files altogether. I told a friend of mine that he ought to
        drop 6 months of zope work and go with cherrypy. ;-)"
        </i><br>
        <a class=moduleLink href="http://sourceforge.net/mailarchive/forum.php?thread_id=2580389&forum_id=9986">Darryl Caldwell on Jun 13, 2003</a>
        <br><br>
        <i>
        "We've chosen to deploy with CherryPy, a fantastic open-source tool. [...] It makes putting together a
        dynamic, object oriented site a quick and painless proposition. It's extremely flexible and offers a fresh way
        to approach site design without all the overhead of a big CMS. [...] Every time I thought I'd have to write a
        utility class from scratch, I've discovered that the functionality was already built in"
        </i><br>
        Steve Nieker from the Waypath project on Mar 17, 2003
        <br><br>
        <i>
        "What's so exciting about CherryPy is that is lowers the floor for web programming while raising the power. [...]
        It also unifies a collection of often difficult tools into a coherent methodology without sacrificing power. [...]
        Perhaps most exciting, CherryPy's approach means that the kind of quick hacks that programmers do for fun
        or curiosity can now include complete web-served applications. That's just the kind of ease-of-creation that
        will foster the exploration of distributed, edge computing."
        </i><br>
        <a class=moduleLink href="http://garyboone.com/categories/theUniversalMachine/2003/03/09.html">Gary Boone on Mar 09, 2003</a>
        <br><br>
        <i>
        "Finally something in this field that seems
        clean, simple and effective! I've looked at a number of
        systems like ZOPE, Quixhote, Webware etc, and this is
        the first that that made me feel that it's just what
        I wanted."
        </i><br>
        Magnus Lycka on Aug 08, 2002
        <br><br>
        <i>
        "I like the ideas behind CherryPy immensely."
        </i><br>
        Tim Jarman on Jul 17, 2002
        <br><br>
        <i>
        "I have to say cherrypy is really quite interesting. Rather different from a 
        lot of things out there."
        </i><br>
        Mukhsein Johari on Jul 28, 2002
        <br><br>
        <i>
        "CherryPy is simple, beautiful, elegant and awesome. I've always wanted something like this, but I was technically not capable of pulling it off myself. But now my seach is over.
        Thank you for making available and sharing just a wonderful piece of creation."
        </i><br>
        Sammy from Vancouver on Aug 05, 2002
        <br><br>
        <i>
        "I'am just starting with CherryPy and I like it to much, it work much at the style of my
        brain than zope. [...] Thanks for this great tool."
        </i><br>
        <a class=moduleLink href="http://sourceforge.net/mailarchive/forum.php?thread_id=944866&forum_id=9986">Cristian Echeverria on Aug 01, 2002</a>

    def search(self, keyWord=''):
        <py-eval="self.header('Search result')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('Search result', self.searchResultContent(keyWord))">
            </td>
        <py-eval="self.footer()">

    def searchResultContent(self, keyWord):
        <py-if="not keyWord.split()">
            <b>You must specify a keyWord</b>
        </py-if>
        <py-else>
            <py-exec="searchResult=self.getSearchResult(keyWord)">
            <py-if="not searchResult"><b>Sorry, no result found for "<py-eval="keyWord">".</b></py-if>
            <py-for="url, title, score in searchResult">
                <py-if="_index==0">
                    <b><py-eval="_end+1"> result<py-if="_end>0">s</py-if> found for "<py-eval="keyWord">":</b><br><br>
                    <table>
                        <tr>
                            <td class=moduleText><b>Title</b></td>
                            <td width=40 class=moduleText>&nbsp;</td>
                            <td class=moduleText><b>Score</b></td>
                        </tr>
                </py-if>
                <tr>
                    <td><a class=moduleLink py-attr="url" href="" py-eval="title"></a></td>
                    <td width=40 class=moduleText>&nbsp;</td>
                    <td class=moduleText py-eval="score"></td>
                </tr>
                <py-if="_index==_end">
                    </table>
                </py-if>
            </py-for>
        </py-else>

    def cherryForum(self):
        <py-eval="self.header('CherryForum')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('CherryForum', self.cherryForumContent())">
            </td>
        <py-eval="self.footer()">
    def cherryForumContent(self):
        <b>CherryForum</b> is a web forum written using <b>CherryPy</b> as well as the new framework
        I'm working on: <b>CherryObjects</b>.<br>
        #This new framework is still under development and I'm hoping to make a beta release in a few weeks (the source
        #code for CherryForum will be release at the same time).<br>
        The source code for CherryObjects and CherryForum will be released when it's stabilized a bit (it is evolving
        quite rapidly at the moment), and when I find the time to do it ...<br>
        In the mean time, I've put online an instance of CherryForum that will be used as:
        <ul>
        <li>A web forum for the CherryPy community, where people can ask questions about CherryPy</li>
        <li>A web forum for CherryForum itself, where people can ask questions about CherryForum and ask for new features</li>
        <li>A testbed for CherryForum (as it is still in alpha stage)</li>
        <li>A web forum for CherryObjects (when I make a first release)</li>
        </ul>
        This web forum can be found <a class=moduleLink py-attr="request.base+'/myForum/index'" href="">here</a>
        <br><br>
        <b>CherryForum documentation</b>:<br>
        CherryForum is still in beta stage and the number of features is limited.<br>
        Here are a few tips that you can use when typing your posts:<br>
        <ul>
        <li><b>HTML code</b>: you can safely type HTML code (special characters will be escaped when the post is rendered)</li>
        <li><b>Links</b>: when you want to put a link in your post, just type the url, starting with "http://" and CherryForum
        will automatically recognize this as a link</li>
        </li>
    def europython2003(self):
        <py-eval="self.header('CherryPy at EuroPython 2003')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('CherryPy at EuroPython 2003', self.europython2003Content())">
            </td>
        <py-eval="self.footer()">
    def europython2003Content(self):
        The slides I used to give a CherryPy presentation at EuroPython 2003 are available in a PowerPoint format
        <a class=moduleLink py-attr="request.base+'/static/CherryPy-EuroPython2003.ppt'" href="#">here</a> and in a PDF format
        <a class=moduleLink py-attr="request.base+'/static/CherryPy-EuroPython2003.pdf'" href="#">here</a><br>
        Don't expect too much from these slides, as I only had 30 minutes to make them and the presentation could only last
        10 minutes at most ...<br><br>
        As a special bonus, here is a picture of me doing the presentation :-):<br><br>
        <center>
        <img py-attr="request.base+'/static/Cherrypy-EuroPython.jpg'" src="">
        </center>

    def cherrypy_0_9_beta(self):
        <py-eval="self.header('Improvements in CherryPy-0.9-beta')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('Improvements in CherryPy-0.9-beta', self.cherrypy_0_9_betaContent())">
            </td>
        <py-eval="self.footer()">
    def cherrypy_0_9_betaContent(self):
        This beta release includes a lot of improvements.<br>
        The new documentation (updated tutorial and HowTos) is included
        when you download the file.<br>
        To download this release, just go to the <a class=moduleLink py-attr="request.base+'/download'" href="">download area</a>.<br>
        This is a beta release, so don't expect it to be bug-free. We count on you to test it and give us some feedback.<br>
        <br>
        <b>Main improvements:</b>
        <ul>
        <li><b>Session handling</b>: This release of CherryPy is the first one to handle sessions. A new HowTo called "How to
        use sessions with CherryPy" explains how it works. A new entry has also been added to the demo to demonstrate this
        new feature. Note that the options for session data storage are restricted for now, but we hope to make more options
        available soon (for instance, the ability to store session data in a database).
        </li>
        <li><b>Python2.3 and Jython compatibility</b>: CherryPy now works with Python2.3 and Jython
        <li><b>Regression test suite</b>: CherryPy now comes with a regression test suite. Please run it on your machine
        and let us know if some tests fail on your machine. Just read "README.TXT" to see how to run the test suite.
        </li>
        <li><b>Default to /index for CherryClasses</b>: If someone types the URL http://domain/dir1/dir2, then CherryPy will
        convert it first to dir1.dir2(), but if there is no such method, it will convert it to dir1_dir2.index(). The tutorial
        has been updated to explain this. (Many thanks to Nolan J. Darilek for this improvement)
        </li>
        <li><b>XML-RPC</b>: The XML-RPC engine has been improved and is now more powerful and robust. The HowTo about XML-RPC
        has been updated to explain how XML-RPC now works. (Many thanks to Steven Nieker for this improvement)
        </li>
        <li><b>Filename extension for <py-eval="'py-'+'include'"></b>: An annoying bug was forcing users to call their template files "*.cpyt"
        when using them in a "<py-eval="'py-'+'include'">". This has been fixed and you can now use any extension you want.
        </li>
        <li><b>Better cookie support</b>: CherryPy now uses the standard "Cookie" module from python (in particular, the
        "SimpleCookie" object type) to handle cookies. A new HowTo called "HowTo use cookies with CherryPy" has been added
        to the documentation.
        </li>
        <li><b>Easier way to run cherrypy.org on your machine</b>: The tar file comes with the source code for the
        cherrypy.org website. Everyone can now easily run this site on their local machine (even if they don't have a
        database installed). Just read "README.TXT" to see how to compile it and run it.
        </li>
        <li><b>Easier way to get logged in user in HttpAuthenticate and CookieAuthenticate</b>: It is now easier to find
        out which user is logged in when using these 2 modules. The documentation and the demo for these modules has been
        updated to show how it is done.
        </li>
        <li><b>"hidden" property now inherited</b>: If you declare a hidden CherryClass or a hidden mask and view and
        then you declare a CherryClass that inherits from the first one, then the "hidden" property is now inherited as
        well by default. The HowTo about hidden masks and views has been updated to explain how it works. Many thanks
        to Scott Luck for this improvement.
        </li>
        </ul>
        For a complete list of improvements, please refer to the ChangeLog.txt file included in the release.<br>
        <br>
        <b>Backward incompatibilities:</b>
        <ul>
        <li><b>XML-RPC</b>: If you were using XML-RPC with cherrypy-0.8, chances are your code won't work anymore with this
        release. So you should read the updated HowTo about XML-RPC to learn how XML-RPC now works.
        </li>
        <li><b>New cookie handling</b>: "cookieMap" is no longer available. You should now use "simpleCookie". Check out the
        new HowTo about how to use cookies with CherryPy to learn how it works.
        </li>
        <li><b>Default to /index for CherryClasses</b>: A few sites might be affected by this change (but only if you were
        doing something very unusual with URLs).
        </li>
        </ul>
        <br>
        <b>Future improvements:</b><br>
        Here is a list of improvements I hope to be able to include in the final 0.9 release:
        <ul>
        <li><b>More options for sessions</b>: I hope to be able to implement a lot more options for handling sessions (the
        ability to store session data to a database, the ability to specify when session data should be saved, ...)
        </li>
        <li><b>Centralized documentation</b>: I'd like to merge all documentation (tutorial, HowTos, lib) into
        a single documentation with a common master page.
        </li>
        </ul>


    def cherrypy_0_9_gamma(self):
        <py-eval="self.header('What\'s new in CherryPy-0.9-gamma')">
            <td width=80% valign=top align=center>
                <py-eval="self.square('What\'s new in CherryPy-0.9-gamma', self.cherrypy_0_9_gammaContent())">
            </td>
        <py-eval="self.footer()">
    def cherrypy_0_9_gammaContent(self):
        This gamma release includes a lot of improvements/bug fixes.<br>
        The new documentation (updated tutorial and HowTos) is included
        when you download the file.<br>
        To download this release, just go to the <a class=moduleLink py-attr="request.base+'/download'" href="">download area</a>.<br>
        To find out what was new in the previous beta release, check out this page
        <a class=moduleLink py-attr="request.base+'/cherrypy_0_9_beta'" href="#">this page</a><br>
        This is a gamma release, so don't expect it to be bug-free. We count on you to test it and give us some feedback.<br>
        <br>
        <b>New features:</b>
        <ul>
        <li><b>Thread-pool server</b>: This release allows you to run the HTTP server in a thread-pool mode: a fixed
        number of threads is created at start-up and these threads handle the requests. To find out about the
        new configuration options, check out the chapter "Deploying your website for production" of the tutorial.
        </li>
        <li><b>Sessions fixed</b>: A bug that caused session data to disappear unexpectedly has been fixed</li>
        <li><b>Ability to store session data in a database</b>: Check out the HowTo about sessions to learn how
        to do that.
        </li>
        <li><b>New HowTo about using Cheetah templates</b></li>
        <li><b>DCOracleFull.cpy</b>: New library module for accessing an Oracle database (thanks to Brent Fentem)</li>
        <li><b>socketQueueSize in config file</b>: New configuration option called "socketQueueSize" to control
        the size of the socket queue (default is 5)</li>
        <li><b>reverseDNS in config file</b>: New configuration option to enable/disable reverse DNS (default is disabled)</li>
        <li><b>Handling of "Last-Modified" and "If-Modified-Since" for static content</b>: This allows the browser
        to cache static data like images</li>
        </ul>
        For a complete list of improvements, please refer to the ChangeLog.txt file included in the release.<br>
        <br>
        <b>Backward incompatibilities:</b>
        <ul>
        <li><b>Aspects</b>: In aspect headers, the keyword "function" has been replaced with the more generic keyword
        "method". So instead of writing "function.name=='...'", you now have to write "method.name='...'".<br>
        A new attribute called "className" has been added as well.
        </li>
        <li><b>fixedNumberOfProcesses</b>: The configuration file option "fixedNumberOfProcesses" is now
        called "processPool".
        </li>
        </ul>

    def previewMessage(self, text, **kw):
        <html>
        <head>
            <title>CherryPy : Message preview</title>
            <style type="text/css"> 
            <!--
            .moduleTitle {font-size:14px; font-weight:bold; color:white; font-family:arial}
            .moduleLink {font-size:12px; color:#BD1E26; font-family:arial} 
            .moduleLink:hover {font-size:12px; color:red; font-family:arial} 
            .moduleLinkB {font-size:12px; font-weight:bold; color:#BD1E26; font-family:arial} 
            .moduleLinkB:hover {font-size:12px; font-weight:bold; color:red; font-family:arial} 
            .moduleText {font-size:12px; color:black; font-family:arial}
            .moduleTextB {font-size:12px; font-weight:bold; color:#BD1E26; font-family:arial}
            --> 
            </style>
        </head>
        <body bgcolor=white topmargin="0" marginheight="0">
            <center>
            <table border=0 cellspacing=0 cellpadding=0 width=60%><tr><td align=center>
                <br>
                <py-eval="self.square('Message preview', cherryPyForumDesign.cookText(text))">
                <br>
                <form action="">
                <input type=submit value="Close this window" onClick="window.close();">
                </form>
            </td></tr></table>
            </center>
        </body>
        

view:
    def leftColumn(self):
        l='''
            <a class=moduleLinkB href="/">Home</a><br>
            <a class=moduleLinkB href="/download">Download</a><br>

            <span class=moduleTextB>Documentation:</span><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/static/html/tut/index.html">Tutorial</a> <small>(start here)</small><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/static/html/howto/index.html">HowTo</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/static/html/lib/index.html">Standard library</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/downloadableDoc">Downloadable/printable format</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/articles">Articles about CherryPy</a><br>

            <span class=moduleTextB>Showcase:</span><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/demo/index">Online demo</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/talk">Testimonials</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/aboutSite">About this site</a><br>

            <span class=moduleTextB>About CherryPy:</span><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/license">License</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/people">People behind CherryPy</a><br>

            <span class=moduleTextB>Getting help:</span><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/mailingLists">Mailing lists</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/myForum/index">Forum</a><br>

            <span class=moduleTextB>Developers:</span><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/cvs">CVS</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="http://sourceforge.net/tracker/?atid=479346&group_id=56099&func=browse">Bug tracker</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="http://sourceforge.net/tracker/?atid=479349&group_id=56099&func=browse">Feature requests</a><br>

            <span class=moduleTextB>Resources:</span><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="/thirdParty">Bakery</a> <small>(third-party modules)</small><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="http://wiki.cherrypy.org/cgi-bin/moin.cgi">Wiki</a> <small>(contributed by users)</small><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="http://wiki.cherrypy.org/cgi-bin/moin.cgi/HostingProviders">CherryPy hosting providers</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="http://wiki.cherrypy.org/cgi-bin/moin.cgi/TipsAndHowTos">User-contributed HowTos</a><br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a class=moduleLink href="http://wiki.cherrypy.org/cgi-bin/moin.cgi/OtherLanguages">Non-english resources</a><br>
        '''
            

##            <a class=moduleLink href="%s/about">About</a><br>
#            <a class=moduleLink href="%s/license">License</a><br>
#            <a class=moduleLink href="%s/documentation">Documentation</a><br>
#            <a class=moduleLink href="%s/download">Download</a><br>
#            <a class=moduleLink href="%s/mailingLists">Mailing lists</a><br>
#            <a class=moduleLink href="%s/cvs">CVS</a><br>
#            <a class=moduleLink href="%s/demo/index">Small online demo</a><br>
#            <a class=moduleLink href="%s/talk">They talk about CherryPy</a><br>
#            <a class=moduleLink href="%s/myForum/index">Forum</a><br>
#        ''' % ((request.base,) * 10)
        return self.leftSquare("CherryPy", l)

function:
    def getSearchResult(self, keyWord):
        # Strip non-common characters
        for i in range(len(keyWord)):
            c=keyWord[i]
            if (not 'a'<=c<='z') and (not 'A'<=c<='Z') and (not '0'<=c<='9'):
                keyWord=keyWord[:i]+' '+keyWord[i+1:]
        keyWordList=keyWord.split()
        result=keyWordMap.get(keyWordList[0], [])
        # Merge with results from other keyWords (if any)
        for keyWord in keyWordList[1:]:
            currentResult=keyWordMap.get(keyWord, [])
            # Compute intersection of result and currentResult. Store result in newResult
            newResult=[]
            for url, title, score in result:
                for url2, title2, score2 in currentResult:
                    if url==url2: newResult.append((url, title, score+score2))
            result=newResult
        if len(keyWordList)>1:
            # Get average scores
            newResult=[]
            for (url, title, score) in result:
                score=float(score)/len(keyWordList)
                score=int(score*10)/10.0
                newResult.append((url, title, score))
            result=newResult
        result.sort(self.sortOnThirdCriteria)
        return result
    def sortOnThirdCriteria(self, tuple1, tuple2):
        if tuple1[2]<tuple2[2]: return 1
        return -1

def initThread(threadIndex):
    time.sleep(threadIndex * 0.1) # Sleep 0.1 second between each new database connection to make sure MySql an keep up
    request.hasDatabase = 1
    try:
        global MySQLdb
        import MySQLdb
        request.connection = MySQLdb.connect(
            configFile.get('database', 'host'),
            configFile.get('database', 'user'),
            configFile.get('database', 'password'),
            configFile.get('database', 'name')
        )
    except: request.hasDatabase=0
    print "hasDatabase:", request.hasDatabase

    # On the production machine, switch user to "cherrypy"
    if configFile.get('restrictedArea', 'login') != 'login':
        os.setegid(2524) 
        os.seteuid(2524)

CherryClass Sql:
function:
    def query(self, query):
        if not request.hasDatabase: return
        c=request.connection.cursor()
        c.execute(query)
        res=c.fetchall()
        c.close()
        print "query:", query, "res:", res
        return res
    def logPageStat(self):
        if not request.hasDatabase: return
        ip=request.headerMap.get('remote-addr', '')
        server=request.headerMap.get('remote-host', '')
        previousPage=request.headerMap.get('referer', '')
        self.query('insert into cherrypy_stat values ("%s", "%s", "%s", "%s",     "%s")'%(
            ip, server, previousPage, request.browserUrl, frenchTools.getNow()))

CherryClass ViewStat(HttpAuthenticate):
function:
    def getPasswordListForLogin(self, login):
        if login==configFile.get('restrictedArea', 'login'): return [configFile.get('restrictedArea', 'password')]
        return []
mask:
    def index(self):
        <html><body>
            <a href="viewPage">Voir les pages</a><br>
            <a href="viewStat?day=today">Voir les stats pour aujourd'hui</a><br>
            <a href="viewStat?day=yesterday">Voir les stats pour hier</a><br>
        </body></html>
view:
    def viewPage(self, start=0, end=100):
        start=int(start)
        end=int(end)
        res=sql.query('select * from cherrypy_stat order by creationTime desc limit 500')
        page="<table border=1><tr><th>Ip</th><th>Host</th><th>Referrer</th><th>Url</th><th>Time</th></tr>"
        for ip, host, referrer, url, time in res[start:end]:
            page+="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(
                ip, host, referrer, url, time)
        link='<a href="%s/viewPage?start=%s&end=%s">See next 100 pages</a>'%(self.getPath(), start+100, end+100)
        return "<html><body>"+page+"</table>%s</body></html>"%link
    def viewStat(self, day):
        if day=='today':
            date=frenchTools.getNow()
            year, month, myDay=int(date[:4]), int(date[5:7]), int(date[8:10])
        else:
            date=frenchTools.getNowMinus(1)
            year, month, myDay=int(date[:4]), int(date[5:7]), int(date[8:10])
        res=sql.query('select count(distinct(ip)) from cherrypy_stat where creationTime between "%s/%s/%s 00:00:00" and "%s/%s/%s 23:59:59"'%(
            year, month, myDay, year, month, myDay))
        user=res[0][0]
        res=sql.query('select count(*) from cherrypy_stat where creationTime between "%s/%s/%s 00:00:00" and "%s/%s/%s 23:59:59"'%(
            year, month, myDay, year, month, myDay))
        page=res[0][0]
        return "<html><body>Visiteurs:%s<br>Pages vues:%s</body></html>"%(user, page)

