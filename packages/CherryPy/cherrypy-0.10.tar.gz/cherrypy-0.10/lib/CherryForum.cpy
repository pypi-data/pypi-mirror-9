use CherryObjectsWeb, Tools, Mail

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

def initProgram():
    import sys, os
    global CherryObjects
    sys.path.append(os.path.join('..', 'lib'))
    import CherryObjectsZODB as CherryObjects

def initServer():
    objectsTypeMap={
        "forum":  {
            "name": "string",
            "description": "text",
            "order": "float",
            "threadList": "list of links to thread.forum linkBack"
        },
        "thread": {
            "subject": "string",
            "forum": "link to forum.threadList",
            "messageList": "list of links to message.thread linkBack",
            "views": "float",
            "creationDate": "string"
        },
        "message": {
            "name": "string",
            "email": "string",
            "sendNotice": "boolean",
            "date": "string",
            "dummySubject": "string",
            "text": "text",
            "thread": "link to thread.messageList"
        }
    }
    objectsTuneMap={
        "thread": {
            "global": {"label": "object.subject"}
        },
        "message": {
            "name": {"validate": CherryObjects.notEmpty},
            "text": {"validate": CherryObjects.notEmpty}
        }
    }
    fname=configFile.get("forum", "dbFile")
    #os.system('rm -fr '+fname)
    CherryObjects.initWeb(fname, objectsTypeMap, objectsTuneMap)

    print "All messages:", message.getObjects()
    for m in message.getObjects():
        message.saveObject(m)

    #f1=forum.newObject(name="Forum 1", description="This is the first forum", order=2)
    #f2=forum.newObject(name="Forum 2", description="This is the second forum", order=1)

    #t1=thread.newObject(subject="Test thread f1", creationDate=tools.getNow(), forum=f1)

    #m1=message.newObject(name="remi", email="remi@cherrypy.org", date=tools.getNow(), text="Mon 1er message", thread=t1)

CherryClass CherryForumAdmin(CherryObjectsWeb) abstract:

CherryClass CherryForum abstract:
function:
    def normalize(self, s):
        newS=""
        for c in s.lower():
            if '0'<=c<='9' or 'a'<=c<='z': newS+=c
            else: newS+=" "
        return newS
    def isKeywordListInString(self, keywordList, str_):
        str_=self.normalize(str_)
        for keyword in keywordList:
            if str_.find(keyword)==-1: return 0
        return 1
    def searchKeywordList(self, keywordList):
        res=[]
        # Search keywords in threads
        for threadObj in thread.getObjects():
            if self.isKeywordListInString(keywordList, threadObj.subject):
                res.append(threadObj)
        # Search keywords in messages
        for messageObj in message.getObjects():
            if self.isKeywordListInString(keywordList, messageObj.text):
                res.append(messageObj.thread)
        return res

    def checkEmailAndNotice(self, object, *kw):
        if object.sendNotice and not object.email: return "Missing"
        if object.email:
            try:
                a,b=object.email.split('@')
                if b.find('.') == -1: raise "error"
            except: return "Wrong email"

mask:
    def index(self):
        <py-eval="self.template.header()">
            <py-code="
                objectList=forum.getObjects()
                CherryObjects.sortOnAttribute(objectList, 'order')
            ">
            <py-eval="forum.viewObjectList(objectList, self.forumListMask)">
        <py-eval="self.template.footer()">

    def search(self, keywordList=""):
        <py-eval="self.template.header()">
        <py-eval="self.template.navigationBar('search')">
        <br>
        <py-eval="self.template.title('Search:')">

        <form py-attr="self.getPath()+'/search'" action="">
        <center>
        Keyword(s): <input type=text name=keywordList py-attr="keywordList" value="">
        <input type=submit value=OK>
        </center>
        </form>
        <py-exec="_keywordList=self.normalize(keywordList).split()">
        <py-if="_keywordList">
            <py-exec="threadList=self.searchKeywordList(_keywordList)">

            <py-eval="self.template.title('%s thread(s) found for keyword(s) %s%s%s:'%(len(threadList), chr(34), keywordList, chr(34)))">

            <py-eval="self.template.searchResultHeader()">

            <py-for="threadObj in threadList">
                <py-eval="self.template.searchResultObject(threadObj)">
            </py-for>

            <py-eval="self.template.searchResultFooter()">

        </py-if>
        <py-eval="self.template.footer()">

    def viewForum(self, forumId, msg="", page=0):
        <py-eval="self.template.header()">
        <py-code="
            pageSize = 30
            forumObj=forum.getObjectById(forumId)
            threadList=forumObj.threadList
            CherryObjects.sortOnAttribute(threadList, 'creationDate', reverse=1)
            pageThreadList = threadList[pageSize * int(page):pageSize * (int(page) + 1)]
        ">

        <py-eval="self.template.navigationBar('viewForum', forumObj)">

        <py-eval="self.template.forumHeader(forumObj)">

        <py-if="msg">
            <center><font color="red"><b py-eval="msg"></b></center></font><br><br>
        </py-if>

        <py-eval="message.viewObjectList(pageThreadList, self.threadListMask)">
        <py-eval="self.template.previousNextPage(int(page), pageSize, len(threadList), forumId)">
        <py-eval="self.template.footer()">

    def newThread(self, forumId, hasError=0, validate=0):
        <py-code="
            forumObj=forum.getObjectById(forumId)
            if validate:
                formTuneMap=request.sessionMap['formTuneMap']
                messageObj=formTuneMap['global']['object']

                # Check that it's not just a refresh of the page ...
                # Get last create thread before this one and check if it has the same fields or not
                threadList=forumObj.threadList
                CherryObjects.sortOnAttribute(threadList, 'creationDate', reverse=1)
                lastThread = threadList[0]
                if lastThread.subject == messageObj.dummySubject:
                    return self.viewForum(forumId=forumId, msg="The thread had already been added")

                # Create new thread object
                threadObj=thread.newObject(subject=messageObj.dummySubject, forum=forumObj, views=0, creationDate=tools.getNow())

                # Update message with this thread as the parent
                messageObj.thread=threadObj
                message.saveObject(messageObj)

                # message.printAllObjects()
                # thread.printAllObjects()

                # Notify people that a reply has been posted
                mailSubject='Someone started a new thread "%s"'%threadObj.subject
                mailBody='Hello,\n\n'
                mailBody+='someone started a new thread "%s"\n'%threadObj.subject
                mailBody+='To view this thread, click on the following link:\n'
                mailBody+='%s/viewThread?threadId=%s\n\n'%(self.getPath(), threadObj.id)
                mailBody+='PS: You are receiving this message because you asked to be notified whenever someone posted a reply to this thread'

                # Send e-mail to admin
                if configFile.get("forum", "sendAdminNotice")=="1":
                    myMail.sendMail("forumAdmin@cherrypy.org", "remi@cherrypy.org", "", "text/plain", mailSubject, mailBody)


                return self.viewForum(forumId=forumId, msg="The new thread has been added")
        ">
        <py-eval="self.template.header()">

        <py-eval="self.template.navigationBar('newThread')">

        <py-eval="self.template.forumHeader(forumObj)">

        <py-eval="self.template.title('Start a new thread:')">

        <py-code="
            messageObj=CherryObjects.CherryObject()
            messageObj.date=tools.getNow()

            tuneMap={
                "thread": {"mask": thread.hiddenMask},
                "date": {"mask": thread.hiddenMask},
                "dummySubject": {
                    "mask": self.template.fieldMask,
                    "label": "Subject:",
                    "validate": CherryObjects.notEmpty},
                "name": {
                    "mask": self.template.fieldMask,
                    "label": "Your name:"
                },
                "email": {
                    "mask": self.template.fieldMask,
                    "label": "Your email (optional):",
                    "validate": self.checkEmailAndNotice
                },
                "sendNotice": {
                    "mask": self.template.fieldMask,
                    "label": "Notify me by e-mail when<br>someone posts a reply:"
                },
                "text": {"mask": self.template.textareaMask},
                "submit": {"mask": self.template.submitMask},
                "global": {"fieldOrder": [
                    self.template.formHeader(),
                    "field name", "field email", "field sendNotice", "field dummySubject",
                    self.template.formSeparator(),
                    "field text", "field submit",
                    self.template.formFooter()]}
            }
        ">
        <py-if="hasError">
            <center><font color=red><b>Please correct the errors below</b></font></center><br><br>
        </py-if>
        <py-eval="message.editObjectForm(messageObj, hasError, self.getPath()+'/newThread?forumId='+forumId+'&validate=1', self.getPath()+'/newThread?forumId='+forumId, tuneMap)">
        <py-eval="self.template.footer()">

    def viewThread(self, threadId, hasError=0, validate=0):
        <py-eval="self.template.header()">

        <py-code="
            threadObj=thread.getObjectById(threadId)
            threadObj.views+=1
            thread.saveObject(threadObj)
            messageList=threadObj.messageList
            CherryObjects.sortOnAttribute(messageList, 'date')
        ">

        <py-eval="self.template.navigationBar('viewThread', threadObj.forum)">

        <py-eval="self.template.forumHeader(threadObj.forum)">

        <py-if="hasError">
            <center><font color=red><b>Please correct the errors below</b></font></center><br><br>
        </py-if>
        <py-if="validate">
            <center><font color=red><b>Your comment has been added</b></font></center><br><br>
            <py-code="
                # Notify people that a reply has been posted
                mailSubject='Someone posted a reply to the thread "%s"'%threadObj.subject
                mailBody='Hello,\n\n'
                mailBody+='someone posted a reply to the thread "%s"\n'%threadObj.subject
                mailBody+='To view this thread, click on the following link:\n'
                mailBody+='%s/viewThread?threadId=%s\n\n'%(self.getPath(), threadId)
                mailBody+='PS: You are receiving this message because you asked to be notified whenever someone posted a reply to this thread'

                # Send e-mail to admin
                if configFile.get("forum", "sendAdminNotice")=="1":
                    myMail.sendMail("forumAdmin@cherrypy.org", "remi@cherrypy.org", "", "text/plain", mailSubject, mailBody)

                # Loop through messages to see if someone needs to be notified
                if configFile.get("forum", "sendNotice")=="1":
                    sendEmailList=[] # To avoid sending 2 e-mails to someone
                    messageObj=request.sessionMap['formTuneMap']['global']['object']
                    myEmail=messageObj.email.lower()
                    for messageObj in threadObj.messageList:
                        if messageObj.sendNotice==1 and messageObj.email.lower()!=myEmail and messageObj.email.lower() not in sendEmailList:
                            try: myMail.sendMail("forumAdmin@cherrypy.org", messageObj.email, "remi@cherrypy.org", "text/plain", mailSubject, mailBody)
                            except: pass
                            sendEmailList.append(messageObj.email.lower())
            ">
        </py-if>
        <py-eval="message.viewObjectList(messageList, self.messageListMask)">

        <br>
        <py-eval="self.template.title('Post a reply:')">

        <py-code="
            messageObj=CherryObjects.CherryObject()
            messageObj.date=tools.getNow()
            messageObj.thread=threadObj
            subject=self.template.fieldMask("Subject:", "dummy", "Re: "+messageObj.thread.subject, "display", "", "", "")

            tuneMap={
                "thread": {"mask": thread.hiddenMask},
                "date": {"mask": thread.hiddenMask},
                "dummySubject": {"mask": thread.hiddenMask},
                "name": {
                    "mask": self.template.fieldMask,
                    "label": "Your name:"
                },
                "email": {
                    "mask": self.template.fieldMask,
                    "label": "Your email (optional):",
                    "validate": self.checkEmailAndNotice
                },
                "sendNotice": {
                    "mask": self.template.fieldMask,
                    "label": "Notify me by e-mail when<br>someone posts a reply:"
                },
                "text": {"mask": self.template.textareaMask},
                "submit": {"mask": self.template.submitMask},
                "global": {"fieldOrder": [
                    self.template.formHeader(),
                    "field name", "field email", "field sendNotice",
                    subject, self.template.formSeparator(),
                    "field text", "field submit",
                    self.template.formFooter()]}
            }
        ">
        <py-eval="message.editObjectForm(messageObj, hasError, self.getPath()+'/viewThread?threadId='+threadId+'&validate=1', self.getPath()+'/viewThread?threadId='+threadId, tuneMap)">

        <py-eval="self.template.footer()">

    def messageListMask(self, object, index, end):
        <py-if="index==0">
            <py-eval="self.template.messageListHeader(object)">
        </py-if>
        <py-eval="self.template.messageListObject(object, index)">

        <py-if="index==end">
            <py-eval="self.template.messageListFooter()">
        </py-if>

    def forumListMask(self, object, index, end):
        <py-if="index==0">
            <py-eval="self.template.forumListHeader()">
        </py-if>
        <py-code="
            # Compute nb threads, nb posts, last post date
            threadList=object.threadList
            if not threadList:
                lastPost="&nbsp;"
                messageList=[]
            else:
                messageList=[]
                for thread in threadList: messageList+=thread.messageList
                CherryObjects.sortOnAttribute(messageList, 'date')
                if not messageList: lastPost="&nbsp;"
                else: lastPost=messageList[-1].date
        ">
        <py-eval="self.template.forumListObject(object, messageList, threadList, lastPost)">
        <py-if="index==end">
            <py-eval="self.template.forumListFooter()">
        </py-if>

    def threadListMask(self, object, index, end):
        <py-if="index==0">
            <py-eval="self.template.threadListHeader(object)">
            #<th class="PhorumTableHeader" align="center" width="40">Views</th>
        </py-if>
        <py-code="
            # Compute last post
            messageList=object.messageList
            CherryObjects.sortOnAttribute(messageList, 'date')
            lastPost=messageList[-1].date
        ">
        <py-eval="self.template.threadListObject(object, lastPost)">
        #<td class="PhorumTableRow" align="center" py-eval="int(object.views)"></td>
        <py-if="index==end">
            <py-eval="self.template.threadListFooter()">
        </py-if>

CherryClass MyMail(Mail):
function:
    def __init__(self):
        self.smtpServer=configFile.get("mail","smtpServer")

