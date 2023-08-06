use Tools

CherryClass CherryPyForumDesign hidden:
mask:
    def header(self):
        <html><head><title>CherryPy Forum</title>
        <style type="text/css">
        <!--
        .moduleTitle {font-size:14px; font-weight:bold; color:white; font-family:arial}
        .moduleLink {font-size:12px; color:#BD1E26; font-family:arial}
        .moduleLink:hover {font-size:12px; color:red; font-family:arial}
        .moduleText {font-size:12px; color:black; font-family:arial}
        -->
        </style>
        </head>
        <body>

    def footer(self):
        </body></html>

    def title(self, title):
        <b py-eval="title"></b><br><br>

    def previousNextPage(self, page, pageSize, totalCount, forumId):
        <py-code="
            if totalCount <= pageSize: return ""
            pageCount = (totalCount - 1) / pageSize + 1
        ">
        <br>
        <table border=0 cellspacing=0 cellpadding=0 width=100%><tr>
        <td align=left>
            &nbsp;
            <py-if="page != 0">
                <a class=moduleLink py-attr="'viewForum?forumId=%s&page=%s' % (forumId, page-1)" href="">&lt;&lt; Previous page</a>
            </py-if>
        </td>
        <td align=right>
            <py-if="page < pageCount - 1">
                <a class=moduleLink py-attr="'viewForum?forumId=%s&page=%s' % (forumId, page+1)" href="">Next page &gt;&gt;</a>
            </py-if>
            &nbsp;
        </td>
        </tr></table>

    def navigationBar(self, page, forumObj=None):
        <table border=0 cellspacing=0 cellpadding=1 width=100%><tr>
            <td width=20% bgcolor=#BD1E26 align=left class=moduleTitle>&nbsp;Goto:</td>
            <td width=80% bgcolor=#FFCCCC class=moduleText>&nbsp;&nbsp;&nbsp;&nbsp;

                <a class=moduleLink href="index">Forum List</a>

                <py-if="page=='viewForum'">
                    &nbsp;&nbsp;&bull;&nbsp;&nbsp;
                    <a class=moduleLink py-attr="'newThread?forumId=%s'%forumObj.id" href="">New Thread</a>
                </py-if>

                <py-if="page=='viewThread'">
                    &nbsp;&nbsp;&bull;&nbsp;&nbsp;
                    <a class=moduleLink py-attr="'viewForum?forumId=%s'%forumObj.id" href="">Thread List</a>
                </py-if>

                #&nbsp;&nbsp;&bull;&nbsp;&nbsp;
                #<a class=moduleLink href="search">Search</a>
            </td>
        </tr></table>

    def forumListHeader(self):
        <py-eval="self.navigationBar('index')">

        <table border=0 cellspacing=1 cellpadding=3 width=100%>
        <tr>
            <td bgcolor=#BD1E26 class=moduleTitle>Forum</td>
            <td bgcolor=#BD1E26 class=moduleTitle>Posts</td>
            <td bgcolor=#BD1E26 class=moduleTitle>Threads</td>
            <td bgcolor=#BD1E26 class=moduleTitle>Last post</td>
        </tr>

    def forumListObject(self, object, messageList, threadList, lastPost):
        <tr>
            <td class=moduleText><a class=moduleLink py-attr="'viewForum?forumId=%s'%object.id" href="" py-eval="object.name"></a><br>
                <py-eval="object.description"></td>
            <td class=moduleText py-eval="len(messageList)"></td>
            <td class=moduleText py-eval="len(threadList)"></td>
            <td class=moduleText py-eval="lastPost"></td>
        </tr>

    def forumListFooter(self):
        </table>

    def forumHeader(self, forumObj):
        <a class=moduleLink py-attr="'viewForum?forumId=%s'%forumObj.id" href="" py-eval="forumObj.name"></a><br>
        <py-eval="tools.escapeHtml(forumObj.description)"><br><br>

    def threadListHeader(self, object):
        <table border=0 cellspacing=1 cellpadding=3 width=100%>
        <tr>
            <td bgcolor=#BD1E26 class=moduleTitle>Subject</td>
            <td bgcolor=#BD1E26 class=moduleTitle>Posts</td>
            <td bgcolor=#BD1E26 class=moduleTitle>Views</td>
            <td bgcolor=#BD1E26 class=moduleTitle>Started By</td>
            <td bgcolor=#BD1E26 class=moduleTitle>Last post</td>
        </tr>

    def threadListObject(self, object, lastPost):
        <tr>
            <td class=moduleText><a class=moduleLink py-attr="'viewThread?threadId=%s'%object.id" href="" py-eval="tools.escapeHtml(object.subject)"></a></td>
            <td class=moduleText py-eval="len(object.messageList)"></td>
            <td class=moduleText py-eval="int(object.views)"></td>
            <td class=moduleText>
                <py-eval="object.messageList[0].name">
                #<py-if="object.messageList[0].email">
                #    (<py-eval="object.messageList[0].email.replace('@',' at ')">)
                #</py-if>
            </td>
            <td class=moduleText py-eval="lastPost"></td>
        </tr>

    def threadListFooter(self):
        </table>

    def messageListHeader(self, object):

    def messageListObject(self, object, index):
        <hr width=100% size=1>
        <b>
            <py-if="index!=0">Re: </py-if>
            <py-eval="tools.escapeHtml(object.thread.subject)">
        </b><br>
        <i>Posted by 
            <py-eval="object.name">
            <py-if="object.email">
                (<py-eval="object.email.replace('@', ' at ')">)
            </py-if>
        on <py-eval="object.date"></i><br><br>
        <py-eval="self.cookText(object.text)">
        <br><br>

    def messageListFooter(self):
        <hr width=100% size=1>

    def searchResultHeader(self):
        <center>
        <br>
        <table>

    def searchResultObject(self, threadObj):
        <tr>
            <td class=moduleText>Thread:</td>
            <td><a class=moduleLink py-attr="'viewThread?threadId=%s'%threadObj.id" href="" py-eval="tools.escapeHtml(threadObj.subject)"></a></td>
            <td width=50>&nbsp;</td>
            <td class=moduleText>in Forum:</td>
            <td><a class=moduleLink py-attr="'viewForum?forumId=%s'%threadObj.forum.id" href="" py-eval="threadObj.forum.name"></a></td>
        </tr>

    def searchResultFooter(self):
        </table>
        </center>

    def formHeader(self):
        <table border=0 cellspacing=0 cellpadding=1><tr><td bgcolor=#000000>
            <table border=0 cellspacing=0 cellpadding=3 bgcolor=#fcfcfc>

    def formFooter(self):
            </table></td></tr>
        </table>

    def formSeparator(self):
        <tr><td colspan=2><hr width=100% size=1></td></tr>

    def textareaMask(self, label, name, fieldValue, typ, error, optionList, extraArgMap):
        <py-if="error">
            <tr><td colspan=2 class=moduleText><font color=red><py-eval="error"></font></td></tr>
        </py-if>
        <tr><td colspan=2>
            <textarea py-attr="name" name="" rows="20" cols="60" py-eval="fieldValue"></textarea>
        </td></tr>
    def submitMask(self, label, name, fieldValue, typ, error, optionList, extraArgMap):
        <tr><td colspan=2 align=right>
            <input type="submit" onClick="document.cherryForm.target='_new'; document.cherryForm.action='/previewMessage';" value=" Preview ">
            &nbsp;&nbsp;&nbsp;&nbsp;
            <input type="submit" onClick="document.cherryForm.target=''; document.cherryForm.action='/message/editObjectFormAction';" value=" Post ">
        </td></tr>

view:
    def fieldMask(self, label, name, fieldValue, typ, error, optionList, extraArgMap):
        res='<tr><td class=moduleText>%s</td><td valign=top class=moduleText>'%label
        if typ=='text':
            res+='<input name="%s" type=text value="%s">'%(name, fieldValue)
        elif typ=='display':
            res+='<input name="%s" type=hidden value="%s">%s'%(name, fieldValue, fieldValue)
        elif typ=='select':
            res+='<select name="%s">'%name
            for optionId, optionLabel in optionList:
                if optionId==fieldValue: res+="<option selected value=%s>%s</option>"%(optionId, optionLabel)
                else: res+="<option value=%s>%s</option>"%(optionId, optionLabel)
            res+='</select>'
        elif typ in ('checkbox','radio'):
            for optionId, optionLabel in optionList:
                res+='<input type="%s" name="%s" value="%s"'%(typ, name, optionId)
                if type(fieldValue)==type([]):
                    if optionId in fieldValue: res+=' checked'
                else:
                    if optionId==fieldValue: res+=' checked'
                res+='>&nbsp;&nbsp;%s<br>'%optionLabel
        if error:
            res+="&nbsp;<font color=red>"+error+"</font>"
        return res+"</td></tr>"

    def cookText(self, text):
        # Escape special characters
        text=text.replace('\r\n','\n')
        while text and text[-1] in ('\n', '\r'): text=text[:-1]
        text=tools.escapeHtml(text)

        i=0
        while 1:
            i=text.find('http://', i)
            if i==-1: break
            j=text.find('&nbsp;',i+1)
            k=text.find(' ', i+1)
            l=text.find('<br>', i+1)
            if j==-1: j=len(text)
            if k==-1: k=len(text)
            if l==-1: l=len(text)
            j=min([j,k,l])
            link=text[i:j]
            linkTag='<a class=moduleLink href="%s">%s</a>'%(link,link)
            text=text[:i]+linkTag+text[j:]
            i+=len(linkTag)
        return text
