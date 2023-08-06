use CherryForum, CherryPyForumDesign, HttpAuthenticate


CherryClass CherryPyOrgForumDesign(CherryPyForumDesign) hidden:
mask:
    def header(self, **kw):
        <py-eval="root.header('CherryPy Forum')">
            <td width=80% valign=top align=center>
                <table border=0 cellspacing=0 cellpadding=0 width=100%>
                    <tr>
                        <td width=10><img py-attr="request.base+'/static/moduleHeaderLeft.gif'" src="" width=10 height=25></td>
                        <td py-attr="request.base+'/static/moduleHeaderMiddle.gif'" background="" height=25 valign=top align=left class=moduleTitle>CherryPy Forum</td>
                        <td width=10><img py-attr="request.base+'/static/moduleHeaderRight.gif'" src="" width=10 height=25></td>
                    </tr><tr>
                        <td width=10 py-attr="request.base+'/static/moduleBodyLeft.gif'" background="">&nbsp;</td>
                        <td class=moduleText>

    def footer(self):
                            <br><br>
                            <table width=100%><tr><td width=100% align=right>
                                <a py-attr="request.base+'/cherryForum'" href=""><img py-attr="request.base+'/static/poweredByCherryForum.gif'" src="" border=0></a>
                            </td></tr></table>
                        </td>
                        <td width=10 py-attr="request.base+'/static/moduleBodyRight.gif'" background="">&nbsp;</td>
                    </tr><tr>
                        <td width=10><img py-attr="request.base+'/static/moduleFooterLeft.gif'" src="" width=10 height=15></td>
                        <td py-attr="request.base+'/static/moduleFooterMiddle.gif'" background="" height=15 py-eval="maskTools.x()"></td>
                        <td width=10><img py-attr="request.base+'/static/moduleFooterRight.gif'" src="" width=10 height=15></td>
                    </tr>
                </table>
            </td>
        <py-eval="root.footer()">

CherryClass MyForum(CherryForum):
function:
    def __init__(self):
        self.template=cherryPyOrgForumDesign

CherryClass MyForumAdmin(CherryForumAdmin,HttpAuthenticate):
function:
    def getPasswordListForLogin(self, login):
        print "login:", login
        if login==configFile.get('restrictedArea', 'login'): return [configFile.get('restrictedArea', 'password')]
        return []

