use HttpAuthenticate, PrestationTables, Mail

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
CherryClass Prestation abstract:
################
#
# Generic class for the prestation website:
#    - this class is subClassed by prestationFrench and prestationEnglish
#

function:
    def localString(self, stri):
        if self==prestationFrench: return stri
        return self.stringMap.get(stri, stri)

    def getNow(self):
        tuple=time.gmtime(time.time())
        return time.strftime('%Y-%m-%d %H:%M:%S', tuple)

    # Return the tag for a single pixel
    def x(self, width=0, height=0):
        if width: width='width=%s'%width
        else: width=''
        if height: height='height=%s'%height
        else: height=''
        if self==prestationFrench: img='xFrench'
        else: img='xEnglish'
        return '<img src="%s/static/%s.gif" %s %s>'%(request.base, img, width, height)

view:
    def header(self):
        if request.path.find('disclaimer')!=-1:
            description=self.localString("Prestation.net - Mentions legales")
            keywords=self.localString("loi, essence")
        elif request.path.find('wapZone')!=-1:
            description=self.localString("Prestation.net - Wap")
            keywords=self.localString("wap, prix")
        elif request.path.find('contactUs')!=-1:
            description=self.localString("Prestation.net - Contactez nous")
            keywords=self.localString("contact, mail")
        elif request.path.find('manager')!=-1:
            description=self.localString("Prestation.net - Devenir gerant")
            keywords=self.localString("gerer, gerant")
        elif request.path.find('firstVisit')!=-1:
            description=self.localString("Prestation.net - Premiere visite")
            keywords=self.localString("premier, visite")
        elif request.path.find('manageStation')!=-1:
            description=self.localString("Prestation.net - Gerer une station")
            keywords=self.localString("gerer, station")
        elif request.path.find('addStation')!=-1:
            description=self.localString("Prestation.net - Ajouter une station")
            keywords=self.localString("ajouter, station")
        elif request.path.find('searchStation')!=-1:
            description=self.localString("Prestation.net - Chercher une station")
            keywords=self.localString("chercher, recherche")
        else:
            description=self.localString("Trouvez la station d'essence la moins chere pres de chez vous")
            keywords=self.localString("essence, super, gasole, gazoil, sans plomb, 95, 98, prix, carburant, pompe, station, pas cher, pas chere")
        return self.headerMask(description, keywords)

    def resultStation(self, zipCode='', city='', keyWord='', department='', type='', sortBy='super', order='asc', page='0'):
        requestTable.addItem(name='zipCode=%s city=%s keyWord=%s department=%s type=%s"'%(zipCode, city,keyWord, department, type), lastUpdateTime=self.getNow())
        param=""
        if zipCode: param+="item.zipCode=='%s' and "%zipCode
        if city: param+="item.city=='%s' and "%city
        if keyWord: param+="item.keyWord.find('%s')!=-1 and "%keyWord.upper()
        if department: param+="item.department=='%s' and "%department
        if type: param+="item.type=='%s' and "%type
        stationList=stationTable.getItem(param[:-5], sortBy, order, lastValueList=[None, 0])
        if not stationList: return self.noStation()
        if len(stationList)>50: return self.tooManyStation()
        else: return self.stationList(stationList, zipCode, city, keyWord, department, type, sortBy, order, int(page))

    def addStationAction(self, myName, zipCode, city, address, phone, open, type, mySupper, sp95, sp98, gazole, nameOrEmail):
        newStationTable.addItem(name=myName, zipCode=zipCode, city=city, address=address, phone=phone, open=open, type=type, super=float(mySupper), sp95=float(sp95), sp98=float(sp98), gazole=float(gazole), nameOrEmail=nameOrEmail, lastUpdateTime=self.getNow())
        return self.header()+"<center><b>Merci de votre contribution.</b><br><br>Les informations que vous avez entrees seront disponibles sur le site sous 24h.</center>"+self.footer()

    def updatePriceAction(self, password, station, mySupper, sp95, sp98, gazole, nameOrEmail):
        if station.gerant and station.gerant!=password:
            return self.header+()+"<center><b>Le mot de passe est incorrect</b><br><br><form><input type=button value='Retour' onClick='javascript:history.back()'></form></center>"+self.footer()
        newPriceTable.addItem(station=station, super=float(mySupper), sp95=float(sp95), sp98=float(sp98), gazole=float(gazole), nameOrEmail=nameOrEmail, lastUpdateTime=self.getNow())
        return self.header()+"<center><b>Merci de votre contribution.</b><br><br>Les informations que vous avez entrees seront disponibles sur le site sous 24h.</center>"+self.footer()

    def updateInfoAction(self, password, station, myName, zipCode, city, address, phone, open, type, nameOrEmail):
        if station.gerant and station.gerant!=password:
            return self.header+()+"<center><b>Le mot de passe est incorrect</b><br><br><form><input type=button value='Retour' onClick='javascript:history.back()'></form></center>"+self.footer()
        newInfoTable.addItem(station=station, name=myName, zipCode=zipCode, city=city, address=address, phone=phone, open=open, type=type, nameOrEmail=nameOrEmail, lastUpdateTime=self.getNow())
        return self.header()+"<center><b>Merci de votre contribution.</b><br><br>Les informations que vous avez entrees seront disponibles sur le site sous 24h.</center>"+self.footer()

    def addCommentAction(self, station, comment, nameOrEmail):
        commentTable.addItem(station=station, comment=comment, nameOrEmail=nameOrEmail, checked=0, lastUpdateTime=self.getNow())
        return self.header()+"<center><b>Merci de votre contribution.</b><br><br>Vos commentaires seront disponibles sur le site sous 24h.</center>"+self.footer()

    def manageStationAction(self, myName, eMail, station, reason, otherReason, password1, password2):
        body=self.localString("Nom")+": %s"%myName
        body+="\n"+self.localString("Email")+": %s"%eMail
        body+="\n"+self.localString("Station")+": %s"%station
        body+="\n"+self.localString("Raison")+": %s"%reason
        body+="\n"+self.localString("Autre raison")+": %s"%otherReason
        body+="\n"+self.localString("Mot de passe")+": %s"%password1
        prestationMail.sendMail('gerer@prestation.net', configFile.get('mail', 'recipient'), '', 'text/plain', 'manageStation', body)
        return (self.header()+
            "<center><b>%s</b><br><br>%s</center>"%(
                self.localString("Votre demande a ete envoyee"), self.localString("Nous vous contacterons d'ici 24 a 72 heures"))
            +self.footer())

mask:

    def addComment(self, station):
        <div py-eval="self.header()"></div>

        <script TYPE="text/javascript">
        
        function checkValues(){
          f=document.commentForm;
          if (f.comment.value.length<3) {alert("<py-eval="self.localString('Vous devez entrer vos commentaires')">"); return false;}
          return true;
        }
        </script>
        
        <center>
        <b py-eval="self.localString('Entrez vos commentaires sur la station')"></b><br><br><br>
        </center>
        
        <FORM name=commentForm method=get py-attr="self.getPath()+'/addCommentAction'" action="#" onSubmit="return checkValues();">
        <input name=station type=hidden py-attr="station" value='#'>
        
        <table border=2 align=center py-attr="self.color2" bgcolor=""><tr><td>
        <TABLE cellspacing=10>

        <TR>
        <TD align=left><B py-eval="'* '+self.localString('Commentaire')+':'"></B></TD>
        <TD align=left><TEXTAREA NAME="comment" COLS=30 ROWS=6 wrap=soft>
        </TEXTAREA></TD>
        </TR>
        <tr><td colspan=2><hr></td></tr>
        <tr>
        <td align=left><B py-eval="self.localString('Votre nom ou e-mail (facultatif)')+':'"></b></td>
        <TD align=left><INPUT TYPE="TEXT" NAME="nameOrEmail" maxlength=40></TD>
        </TR>
        </TABLE></td></tr></table>
        
        <BR>
        <center>
        <INPUT TYPE=submit py-attr="self.localString('Valider')" VALUE="">
        &nbsp;&nbsp;
        <input type=button py-attr="self.localString('Annuler')" VALUE="" onclick="history.back();">
        </center>

        </form>

        <div py-eval="self.footer()"></div>

    def viewComment(self, station):
        <div py-eval="self.header()"></div>
        <div py-exec="commentList=commentTable.getItem('item.station==%s and item.checked==1'%station)"></div>
            <center><h2>
              Il y a <div py-eval="len(commentList)"></div> commentaires sur cette station
            </h2></center>
            <br><hr size=4>
        <div py-for="comment in commentList">
          <div py-eval="comment.comment"></div><br>
          <table width=100%><tr><td align=right>
          <small>
          <div py-if="comment.nameOrEmail!=''">
             Commentaire de <b py-eval="comment.nameOrEmail">nameOrEmail</b>
          </div><div py-else>
             Commentaire anonyme
          </div>
             le <div py-eval="self.formatDateForDay(comment.lastUpdateTime)">Date</div>
          </small>
          </td></tr></table>
          <div py-if="_item_index==len(commentList)-1"><hr size=4>
          </div><div py-else><hr>
          </div>
        </div>
        <div py-eval="self.footer()"></div>

    def updateInfo(self, station):
        <div py-eval="self.header()"></div>

        <script TYPE="text/javascript">

        function checkZipCode(zc){
           if (isNaN(zc) || zc.length!=5 || zc<'01000' || zc>'95999') {
              alert("Le code postal n'est pas valide")
              return false
           }
           return true
        }

        function checkValues(){
          f=document.infoForm;
          if (f.myName.value.length<3) {alert("Vous devez entrer le nom de la station"); return false;}
          if (!checkZipCode(f.zipCode.value)) return false
          if (f.city.value.length<3) {alert("Vous devez entrer une ville"); return false;}
          if (f.address.value.length<3) {alert("Vous devez entrer une adresse"); return false;}
          if (f.type.selectedIndex==0) {alert("Vous devez entrer le type de la station"); return false;}
          if (f.password.value.length<3) {alert("Vous devez entrer le mot de passe"); return false;}
          return true;
        }
        </script>

        <center>
        <B>Si les informations sur la station ne sont pas a jour, vous pouvez les
        modifier grace a la forme ci-dessous</b><br><br>
        Les autres utilisateurs vous en seront reconnaissant<br>
        </center>

        <FORM name=infoForm method=get py-attr="self.getPath()+'/updateInfoAction'" action="#" onSubmit="return checkValues();">
        <input name=station type=hidden py-attr="station" value='#'>

        <table border=2 align=center py-attr="self.color2" bgcolor=""><tr><td>
        <TABLE cellspacing=10>
        <TR>
        <TD align=left><B>* Nom de la station:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="myName" py-attr="station.name" value="#" size=35></TD>
        </TR>
        <TR>
        <TD align=left><B>* Code postal:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="zipCode" py-attr="station.zipCode" value="#" maxlength=5></TD>
        </TR>
        <TR>
        <TD align=left><B>* Ville:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="city" py-attr="station.city" value="#" ></TD>
        </TR>
        <TR>
        <TD align=left><B>* Adresse:</B></TD>
        <TD align=left><TEXTAREA NAME="address" COLS=30 ROWS=3 wrap=soft py-eval="station.address">
        </TEXTAREA></TD>
        </TR>
        <TD align=left><B>Telephone:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="phone" py-attr="station.phone" value="#"  maxlength=14></TD>
        </TR>
        <TR>
        <TD align=left><B>Horaires d'ouverture:</B></TD>
        <TD align=left><TEXTAREA NAME="open" COLS=30 ROWS="2" wrap=soft py-eval="station.open">
        </TEXTAREA></TD>
        </TR>
        <TR>
        <TD align=left><B>* Type de station:</B></TD>
        <TD align=left><SELECT name=type>
        <OPTION></OPTION>
        <div py-for="type in stationTable.getAllTypes()">
          <OPTION
          <div py-if="station.type==type">
            SELECTED
          </div>
          py-eval="type"> type </OPTION>
        </div>
        </SELECT></TD>
        </TR>
        <tr><td colspan=2><hr></td></tr>

        <div py-if="station.gerant==''">
          <tr>
          <td><B>Votre nom ou e-mail (facultatif):</b></td>
          <TD><INPUT TYPE="TEXT" NAME="nameOrEmail" maxlength=40>
            <input type="hidden" name="password" value="abcd"></TD>
          </tr>
        </div><div py-else>
          <tr>
          <td><B>Mot de passe gerant:</b></td>
          <TD><INPUT TYPE="password" NAME="password" maxlength=40>
            <input type="hidden" name="nameOrEmail" value="gerant"></TD>
          </tr>
        </div>

        </TABLE></td></tr></table>

        <BR>
        <center>
        <INPUT TYPE=submit VALUE="Mettre a jour les informations">
        &nbsp;&nbsp;
        <input type=button value=Annuler onclick="history.back();">
        </center>

        </form>

        <div py-eval="self.footer()"></div>

    def updatePrice(self, station):
        <div py-eval="self.header()"></div>

        <script TYPE="text/javascript">

        function checkPrice(str, type) {
           if (str=='') return false
           if (isNaN(str)) return false
           nb=parseFloat(str)
           if (nb==0) return true
           if (nb<0.5 || nb>2) return false
           return true;
        }

        function checkValues(){
          f=document.priceForm;
          if (checkPrice(f.mySupper.value,'super')!=true) {alert("Le prix du super est invalide"); return false;}
          if (checkPrice(f.sp95.value,'sp95')!=true) {alert("Le prix du sans plomb 95 est invalide"); return false;}
          if (checkPrice(f.sp98.value,'sp98')!=true) {alert("Le prix du sans plomb 98 est invalide"); return false;}
          if (checkPrice(f.gazole.value,'gazole')!=true) {alert("Le prix du gazole est invalide"); return false;}
          if (f.password.value.length<3) {alert("Vous devez entrer le mot de passe"); return false;}
          return true;
        }
        </script>

        <center>
        <B>Si les prix du carburant pour cette station ne sont pas a jour, vous pouvez les
        modifier grace a la forme ci-dessous</b><br><br>
        Les autres utilisateurs vous en seront reconnaissant<br>
        </center>

        <FORM name=priceForm method=get py-attr="self.getPath()+'/updatePriceAction'" action="#" onSubmit="return checkValues();">
        <input name=station type=hidden py-attr="station" value='#'>

        <table border=2 align=center py-attr="self.color2" bgcolor=""><tr><td>
        <TABLE cellspacing=10>

        <tr><td colspan=2><br></td></tr>
        <TR>
        <TD align=left><B>* Prix du super:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="mySupper" py-attr="'%01.02f'%station.super" value="#" size=4 maxlength=4> EUR</TD>
        </TR>
        <TR>
        <TD align=left><B>* Prix du sans plomb 95:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="sp95" py-attr="'%01.02f'%station.sp95" value="#" size=4 maxlength=4> EUR</TD>
        </TR>
        <TR>
        <TD align=left><B>* Prix du sans plomb 98:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="sp98" py-attr="'%01.02f'%station.sp98" value="#" size=4 maxlength=4> EUR</TD>
        </TR>
        <TR>
        <TD align=left><B>* Prix du gazole:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="gazole" py-attr="'%01.02f'%station.gazole" value="#" size=4 maxlength=4> EUR</TD>
        </TR>
        <tr><td colspan=2><hr></td></tr>
        <div py-if="station.gerant==''">
          <tr>
          <td align=left><B>Votre nom ou e-mail (facultatif):</b></td>
          <TD align=left><INPUT TYPE="TEXT" NAME="nameOrEmail" maxlength=40>
            <input type="hidden" name="password" value="abcd"></TD>
          </tr>
        </div><div py-else>
          <tr>
          <td align=left><B>Mot de passe gerant:</b></td>
          <TD align=left><INPUT TYPE="password" NAME="password" maxlength=40>
            <input type="hidden" name="nameOrEmail" value="gerant"></TD>
          </tr>
        </div>

        </TABLE></td></tr></table>

        <BR>
        <center>
        <INPUT TYPE=submit VALUE="Mettre a jour les prix">
        &nbsp;&nbsp;
        <input type=button value=Annuler onclick="history.back();">
        </center>

        </form>

        <div py-eval="self.footer()"></div>

    def manageStation(self):
        <div py-eval="self.header()"></div>

        <script language="javascript">

        function checkValues(){
          f=document.manageStationForm;
          if (f.myName.value.length<3) {alert("Vous devez entrer votre nom"); return false;}
          if (f.eMail.value.length<3) {alert("Vous devez entrer votre e-mail"); return false;}
          if (f.station.value.length<3) {alert("Vous devez entrer la station"); return false;}
          if (f.password1.value.length<3) {alert("Vous devez entrer un mot de passe"); return false;}
          if (f.password1.value!=f.password2.value) {alert("Les mots de passe ne sont pas les memes"); return false;}
          return true;
        }
        </script>

        <center><small><b>
        Si vous etes gerant d'une station dans la vie ou que vous voulez tout simplement
        vous occuper d'une station sur notre site, vous pouvez "gerer la station" sur
        le site. Cela signifie que vous seul pourrez mettre a jour les prix ou les
        infos sur cette station (grace a un mot de passe).</b><br><br>
        Il vous suffit de remplir la forme ci-dessous</small><br>

        <FORM name=manageStationForm method=get py-attr="self.getPath()+'/manageStationAction'" action="#" onSubmit="return checkValues();">

        <table border=2 align=center py-attr="self.color2" bgcolor=""><tr><td>
        <TABLE cellspacing=10>
        <TR>
        <TD align=left><B>* Votre nom:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="myName" size=35></TD>
        </TR>
        <TR>
        <TD align=left><B>* Votre e-mail:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="eMail" size=35></TD>
        </TR>
        <TR>
        <TD align=left><B>* Quelle station:<br><small>(Nom, adresse, code postal, ville)</small></B></TD>
        <TD align=left><TEXTAREA NAME="station" COLS=30 ROWS=3 wrap=soft>
        </textarea></TD>
        </TR>
        <TR>
        <TD align=left><B>* Raison pour gerer la<br>station sur le site:</B></TD>
        <TD align=left>
        <input type=radio checked name=reason value=manager>Je suis gerant dans la vie<br>
        <input type=radio name=reason value=other>Autre:
        <input type=text name="otherReason" size=25>
        </TD>
        </TR>
        <TR>
        <TD align=left><B>* Mot de passe:</B></TD>
        <TD align=left><INPUT TYPE="password" NAME="password1"></TD>
        </TR>
        <TR>
        <TD align=left><B>* Confirmation mot de passe:</B></TD>
        <TD align=left><INPUT TYPE="password" NAME="password2"></TD>
        </TR>
        </TABLE></td></tr></table>

        <BR><br>
        <center>
        <INPUT TYPE=submit VALUE="Gerer la station">
        &nbsp;&nbsp;
        <input type=button value=Annuler onclick="history.back();">
        </center>

        </form>

        <div py-eval="self.footer()"></div>

    def stationList(self, stationList, zipCode, city, keyWord, department, type, sortBy, order, page):
        <div py-eval="self.header()"></div>
          <script>
          function openUrl(url) {
            window.open(url,'Plan','')
            return
          }
          </script>
          <center><h3>
          <div py-if="len(stationList)==1">
            Une seule station a ete trouvee pour ces criteres</h3>
          </div><div py-else>
            <div py-eval="len(stationList)"></div> stations ont ete trouvees pour ces criteres</h3>
            <form name=sortForm py-attr="self.getPath()+'/resultStation'" action="#">
            <input type=hidden name=zipCode py-attr="zipCode" value="#">
            <input type=hidden name=city py-attr="city" value="#">
            <input type=hidden name=keyWord py-attr="keyWord" value="#">
            <input type=hidden name=department py-attr="department" value="#">
            <input type=hidden name=type py-attr="type" value="#">
            Classer les stations par
            <select name=sortBy>
            <option value=super
              <div py-if="sortBy=='super'">selected</div>
            >Prix du super</option>
            <option value=sp95
              <div py-if="sortBy=='sp95'">selected</div>
            >Prix du sp95</option>
            <option value=sp98
              <div py-if="sortBy=='sp98'">selected</div>
            >Prix du sp98</option>
            <option value=gazole
              <div py-if="sortBy=='gazole'">selected</div>
            >Prix du gazole</option>
            <option value=zipCode
              <div py-if="sortBy=='zipCode'">selected</div>
            >Code postal</option>
            </select>
            dans l'ordre
            <select name=order>
            <option value=asc
              <div py-if="order=='asc'">selected</div>
            >Croissant</option>
            <option value=desc
              <div py-if="order=='desc'">selected</div>
            >Decroissant</option>
            </select>
            &nbsp;<input type=submit value=GO>
            </form>
          </div>
          </center>

          <table width="100%"><tr><td align=right><small><small>Stations:&nbsp;
            <div py-for="i in range(len(stationList)/5)">
              <div py-exec="request.paramMap['page']=str(i)"></div>
              <div py-if="page!=i"><a py-attr="request.base+'/'+request.path+'?'+urllib.urlencode(request.paramMap)" href="#"></div><div py-eval="'%s-%s'%(i*5+1, i*5+5)"></div><div py-if="i!=page"></a></div>
              &nbsp;
            </div>
            <div py-if="len(stationList)%5">
              <div py-exec="request.paramMap['page']=str(len(stationList)/5)"></div>
              <div py-if="page!=len(stationList)/5"><a py-attr="request.base+'/'+request.path+'?'+urllib.urlencode(request.paramMap)" href="#"></div><div py-eval="'%s-%s'%((len(stationList)/5)*5+1, len(stationList))"></div><div py-if="page!=len(stationList)/5"></a></div>
            </div>
          </small></small></td></tr></table>
          <hr size=4>
          <table align=center width="90%">
          <div py-for="station in stationList[page*5:page*5+5]">
            <div py-debug="'station:%s'%station"></div>
            <tr>
              <td width="100%"><div py-eval="self.viewStation(station)"></div>
            <div py-if="station==stationList[page*5:page*5+5][-1]">
              </td></tr>
            </div><div py-else>
              <hr></td></tr>
            </div>
          </div>
          </table>

          <hr size=4>
          <table width="100%"><tr><td align=left>
            <div py-if="page!=0">
              <div py-exec="request.paramMap['page']=str(page-1)"></div>
              <small><a py-attr="request.base+'/'+request.path+'?'+urllib.urlencode(request.paramMap)" href="#">&lt;&lt; stations precedentes</a></small>
            </div>
          </td><td align=right>
            <div py-if="page!=len(stationList)/5">
              <div py-exec="request.paramMap['page']=str(page+1)"></div>
              <small><a py-attr="request.base+'/'+request.path+'?'+urllib.urlencode(request.paramMap)" href="#">stations suivantes &gt;&gt;</a></small>
            </div>
          </td></tr></table>

        <div py-eval="self.footer()"></div>

    def viewStation(self, station):
        <table width=100% cellspacing=0>
        <tr>
        <td width="40%">
          <a class="updateLink" py-attr="self.getPath()+'/updatePrice?station='+urllib.quote_plus(`station`)" href="#">
          &nbsp;Mettre a jour les prix<div py-if="station.gerant!=''"> (gerant)</div>&nbsp;</a>
        </td><td width="10%"></td>
        <td width="50%">
          <a class="updateLink" py-attr="self.getPath()+'/updateInfo?station='+urllib.quote_plus(`station`)" href="#">
          &nbsp;Mettre a jour les infos<div py-if="station.gerant!=''"> (gerant)</div>&nbsp;</a>
        </td>
        </tr>
        <tr><td>
        <table>
          <tr><td class="gasType">
            <b>SUPER</b>
          </td><td width=42 height=18 py-eval="self.viewPrice(station.super)">
          </td></tr>
          <tr><td class="gasType">
            <b>SP 95</b>
          </td><td py-eval="self.viewPrice(station.sp95)">
          </td></tr>
          <tr><td class="gasType">
            <b>SP 98</b>
          </td><td py-eval="self.viewPrice(station.sp98)">
          </td></tr>
          <tr><td class="gasType">
            <b>GAZOLE</b>
          </td><td py-eval="self.viewPrice(station.gazole)">
          </td></tr>
          <tr><td colspan=2>
            <small><small>
              <div py-if="station.super+station.sp95+station.sp98+station.gazole==0">
                Prix inconnus
              </div><div py-else>
                Mis a jour le
                <div py-eval="self.formatDateForDay(station.lastUpdateTime)">Date</div>
              </div>
            </small></small>
          </td></tr>
        </table>
        </td><td></td>
        <td>
        <table><tr><td align=center width=190>
          <div py-if="station.type!='Autre'">
            <img py-attr="request.base+'/static/%s.gif'%(station.type.replace('e','e'))" src="#">
          </div>
        </td>
        <td align=right>
        <a href="javascript:openUrl('http://www.maporama.com/share/Map.asp?PDT=maposearch?language=fr&_XgoGCAdrCommand=run&_XgoGCAddress=<div py-eval="urllib.quote_plus(station.address)"></div>&Zip=<div py-eval="urllib.quote_plus(station.zipCode)"></div>&_XgoGCTownName=<div py-eval="urllib.quote_plus(station.city)"></div>&COUNTRYCODE=FR')"><img py-attr="request.base+'/static/map.gif'" src="#" border=0 alt="Plan"></a>
        </td></tr></table>
        <b py-eval="station.zipCode+' '+station.city">zipCode city</b><br>
        <b><small py-eval="station.name">name</small></b><br>
        <small py-eval="station.address">address</small><br>
        <small><img py-attr="request.base+'/static/phone.gif'" src="#" py-eval="'&nbsp;'+station.phone"></small><br>
        <div py-if="open!=''">
          <small><b py-eval="'Ouverture '+station.open+'<br>'"></b></small>
        </div>
        </td>
        </tr>
        <tr><td>
          <a class=commentLink py-attr="self.getPath()+'/addComment?station='+urllib.quote_plus(`station`)" href="#">
           Donner mon avis sur cette station</a>
        </td><td></td><td>
          <div py-exec="numberOfComments=len(commentTable.getItem('item.station==%s and item.checked==1'%station))"></div>
          <div py-if="numberOfComments!=0">
            <a class=commentLink py-attr="self.getPath()+'/viewComment?station='+urllib.quote_plus(`station`)" href="#">
             Lire les commentaires sur cette station (<div py-eval="numberOfComments"></div>)</a>
          </div><div py-else>
            <small>Aucun commentaire pour l'instant</small>
          </div>
        </td></tr>
        </table>

    def viewPrice(self, price):
        <div py-if="price==0">
          <img py-attr="request.base+'/static/unknownPrice.gif'" src="#" width=42 height=18>
        </div><div py-else>
          <div py-exec="price='%01.02f'%price"></div>
          <table cellspacing=0 cellpadding=0 border=0><tr>
            <div py-for="i in range(4)">
              <div py-if="i==1">
                <td width=6>
                <img py-attr="request.base+'/static/dot.gif'" src="#" width=6 height=18>
              </div><div py-else>
                <td width=12>
                <img py-attr="request.base+'/static/%s.gif'%price[i]" src="#" width=12 height=18>
              </div>
              </td>
            </div>
          </tr></table>
        </div>

    def searchStation(self):
        <div py-eval="self.header()"></div>
        
        <script TYPE="text/javascript">
        function checkZipCode(zc){
         if (isNaN(zc) || zc.length!=5 || zc<'01000' || zc>'95999') {
            alert("Le code postal n'est pas valide")
            return false
         } else return true
        }
        function checkKeyWord(kw) {
         if (kw.length<3) {
            alert("Le mot clef doit avoir au moins 3 caracteres !")
            return false
         } else return true
        }
        function checkCity(city) {
         if (city.length<3) {
            alert("La ville doit avoir au moins 3 caracteres !")
            return false
         } else return true
        }
        function checkDepartment(id) {
           if (isNaN(id) || id.length!=2 || id<'01' || id>'95') {
              alert("Le departement n'est pas valide")
              return false
           } else return true
        }
        function checkValues(){
          // Check that not all values are empty and that they are correct
          allEmpty=true
          f=document.stationForm
          zc=f.zipCode.value
          if (zc!='') {
            if (!checkZipCode(zc)) return false
            allEmpty=false
          }
          kw=f.keyWord.value
          if (kw!='') {
            if (!checkKeyWord(kw)) return false
            allEmpty=false
          }
          city=f.city.value
          if (city!='') {
            if (!checkCity(city)) return false
            allEmpty=false
          }
          id=f.department.value
          if (id!='') {
            if (id=='2a' || id=='2A' || id=='2b' || id=='2B') id='20'
            if (id.length==1) id='0'+id
            if (!checkDepartment(id)) return false
            f.department.value=id
            allEmpty=false
          }
          if (f.type.selectedIndex!=0) {
            allEmpty=false
          }
          if (allEmpty) {
            alert("Vous devez preciser au moins un critere de recherche")
            return false
          }
          return true
        }
        </script>
        
        <center><b>Entrez un ou plusieurs criteres pour la station.</b></center>
        <br><br><br>
        
        <FORM name=stationForm method="GET" py-attr="self.getPath()+'/resultStation'" action="#" onSubmit="return checkValues()">
        <table border=2 align=center py-attr="self.color2" bgcolor=""><tr><td>
        <TABLE cellspacing=10>
        
        <TR>
        <TD align=left><B>Code postal:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="zipCode" size=5 maxlength=5></TD>
        </TR>
        <TR>
        <TD align=left><B>Ville:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="city"></TD>
        </TR>
        <TR>
        <TD align=left><B>Mot clef:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="keyWord"></TD>
        </TR>
        <TR>
        <TD align=left><B>Departement:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="department" size=3 maxlength=3></TD>
        </TR>
        <TR>
        <TD align=left><B>Type de station:</B></TD>
        <TD align=left><SELECT name=type>
        <OPTION></OPTION>
        <div py-for="type in stationTable.getAllTypes()">
          <div py-if="type!='Autre'">
            <OPTION py-eval="type">Type</OPTION>
          </div>
        </div>
        </SELECT></TD>
        </TR>
        <tr><td colspan=2><hr>Classer les stations par
          <select name=sortBy>
          <option value=super>Prix du super</option>
          <option value=sp95>Prix du sp95</option>
          <option value=sp98>Prix du sp98</option>
          <option value=gazole>Prix du gazole</option>
          <option value=zipCode>Code postal</option>
          </select>
          dans l'ordre
          <select name=order>
          <option value=asc>Croissant</option>
          <option value=desc>Decroissant</option>
          </select>
        </td></tr>
        </TABLE></td></tr></table>
        
        <BR>
        <TABLE align=center>
        <TR><TD>
        <INPUT TYPE=submit VALUE="Lancer la recherche">
        </td></tr></table>
        
        </form>
        
        <div py-eval="self.footer()"></div>

    def addStation(self):
        <div py-eval="self.header()"></div>

        <script TYPE="text/javascript">

        function checkZipCode(zc){
           if (isNaN(zc) || zc.length!=5 || zc<'01000' || zc>'95999') {
              alert("Le code postal n'est pas valide")
              return false
           }
           return true
        }

        function checkPrice(str, type) {
           if (str=='') return false
           if (isNaN(str)) return false
           nb=parseFloat(str)
           if (nb==0) return true
           if (nb<0.5 || nb>2) return false
           return true;
        }
        
        function checkValues(){
          f=document.addStationForm;
          if (f.myName.value.length<3) {alert("Vous devez entrer le nom de la station"); return false;}
          if (!checkZipCode(f.zipCode.value)) return false
          if (f.city.value.length<3) {alert("Vous devez entrer une ville"); return false;}
          if (f.address.value.length<3) {alert("Vous devez entrer une adresse"); return false;}
          if (f.type.selectedIndex==0) {alert("Vous devez entrer le type de la station"); return false;}
          if (checkPrice(f.mySupper.value,'super')!=true) {alert("Le prix du super est invalide"); return false;}
          if (checkPrice(f.sp95.value,'sp95')!=true) {alert("Le prix du sans plomb 95 est invalide"); return false;}
          if (checkPrice(f.sp98.value,'sp98')!=true) {alert("Le prix du sans plomb 98 est invalide"); return false;}
          if (checkPrice(f.gazole.value,'gazole')!=true) {alert("Le prix du gazole est invalide"); return false;}
          return true;
        }
        </script>
        
        <center>
        <b>Si vous connaissez une station qui n'est pas dans notre liste, vous pouvez
        l'ajouter grace a la forme ci-dessous</b><br><br>
        Les autres utilisateurs vous en seront reconnaissant<br>
        </center>

        <FORM name=addStationForm method=get py-attr="self.getPath()+'/addStationAction'" action="#" onSubmit="return checkValues();">

        <table border=2 align=center py-attr="self.color2" bgcolor=""><tr><td>
        <TABLE cellspacing=10>
        <TR>
        <TD align=left><B>* Nom de la station:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="myName" size=35></TD>
        </TR>
        <TR>
        <TD align=left><B>* Code postal:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="zipCode" maxlength=5></TD>
        </TR>
        <TR>
        <TD align=left><B>* Ville:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="city"></TD>
        </TR>
        <TR>
        <TD align=left><B>* Adresse:</B></TD>
        <TD align=left><TEXTAREA NAME="address" COLS=30 ROWS=3 wrap=soft>
        </TEXTAREA></TD>
        </TR>
        <TR><TD align=left><B>Telephone:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="phone" maxlength=14></TD>
        </TR>
        <TR>
        <TD align=left><B>Horaires d'ouverture:</B></TD>
        <TD align=left><TEXTAREA NAME="open" COLS=30 ROWS="2" wrap=soft>
        </TEXTAREA></TD>
        </TR>
        <TR>
        <TD align=left><B>* Type de station:</B></TD>
        <TD align=left><SELECT name=type>
        <OPTION></OPTION>
        <div py-for="type in stationTable.getAllTypes()">
          <OPTION py-eval="type"> type </OPTION>
        </div>
        </SELECT></TD>
        </TR>
        <tr><td colspan=2><hr></td></tr>
        <tr>
        <td align=left><B>Votre nom ou e-mail (facultatif):</b></td>
        <TD align=left><INPUT TYPE="TEXT" NAME="nameOrEmail" maxlength=40></TD>
        </TR>
        </TABLE></td></tr></table>

        <br><br><center><b>Si vous avez connaissez aussi le prix des carburants, vous pouvez le
        donner grace a la forme ci-dessous</b></center><br><br>
        <table border=2 align=center py-attr="self.color2" bgcolor=""><tr><td>
        <TABLE cellspacing=10>

        <tr><td colspan=2><br></td></tr>
        <TR>
        <TD align=left><B>* Prix du super:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="mySupper" value="0.00" size=4 maxlength=4></TD>
        </TR>
        <TR>
        <TD align=left><B>* Prix du sans plomb 95:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="sp95" value="0.00" size=4 maxlength=4></TD>
        </TR>
        <TR>
        <TD align=left><B>* Prix du sans plomb 98:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="sp98" value="0.00" size=4 maxlength=4></TD>
        </TR>
        <TR>
        <TD align=left><B>* Prix du gazole:</B></TD>
        <TD align=left><INPUT TYPE="TEXT" NAME="gazole" value="0.00" size=4 maxlength=4></TD>
        </TR>
        </TABLE></td></tr></table>
        <BR><br>
        <center>
        <INPUT TYPE=submit VALUE="Ajouter la station">
        &nbsp;&nbsp;
        <input type=button value=Annuler onclick="history.back();">
        </center>

        </form>

        <div py-eval="self.footer()"></div>

    def headerColumn(self):
        <table align=center>
            <tr><td align=center><br><br>
            <div py-if="self==prestationFrench">
                <a py-attr="request.base+'/prestationEnglish/index'" href=""><img py-attr="request.base+'/static/englishFlag.jpg'" src="" border=0></a>
            </div><div py-else>
                <a py-attr="request.base+'/prestationFrench/index'" href=""><img py-attr="request.base+'/static/frenchFlag.jpg'" src="" border=0></a>
            </div>
        <br><br>
        <font color=white py-eval="self.getDate()">date</font>
        <br><br></td></tr>
            <tr><td>
              <form method="GET" name="fastSearchForm" py-attr="self.getPath()+'/resultStation'" action="#">
                <table border=0 cellspacing=0 cellpadding=0>
                  <tr><th colspan=3 py-attr="self.color2" bgcolor="" align=center py-eval="self.localString('Recherche rapide')"></th></tr>
                  <tr><td width=1 rowspan=3 py-eval="self.x(1, 110)"></td>      
                    <td class=leftHeaderLink py-eval="'&nbsp;'+self.localString('Code postal')+':'"></td>
                    <td align=right><input type=text name=zipCode size=8 maxLength=5 value="88000" onfocus="value=''">&nbsp;
                      <a href="javascript:document.fastSearchForm.submit()"
                      onClick="return checkFastZipCode()" py-eval="self.go()"></a></td></tr>
                  <tr><td class=leftHeaderLink py-eval="'&nbsp;'+self.localString('Departement')+':'"></td>
                    <td align=right><input type=text name=department size=3 maxLength=2 value="54" onfocus="value=''">&nbsp;
                      <a href="javascript:document.fastSearchForm.submit()"
                      onClick="return checkFastDepartment()"  py-eval="self.go()"></a></td></tr>
                  <tr><td class=leftHeaderLink py-eval="'&nbsp;'+self.localString('Mot clef')+':'"></td>
                    <td align=right><input type=text name=keyWord size=8 value="A 40" onFocus="value=''">&nbsp;
                      <a href="javascript:document.fastSearchForm.submit()"
                      onClick="return checkFastKeyWord()"  py-eval="self.go()"></a></td></tr>
                  <tr><td colspan=3 py-eval="self.x(190, 1)"></td></tr>
                </table>
                <input name=city type=hidden value="">
                <input name=type type=hidden value="">
                <input name=sortBy type=hidden value="super">
                <input name=order type=hidden value="asc">
              </form>
           </td></tr>
            <tr><td><br>
              <table border=0 cellspacing=0 cellpadding=0>
                <tr><th colspan=2 py-attr="self.color2" bgcolor="" align=center py-eval="self.localString('Stations')"></th></tr>
                <tr><td width=1 rowspan=3 py-eval="self.x(1, 90)"></td>
                  <td align=center><a class=leftHeaderLink py-attr="self.getPath()+'/searchStation'" href="#" py-eval="self.localString('Recherche avancee')">
                    </a></td></tr>
                <tr><td align=center><a class=leftHeaderLink py-attr="self.getPath()+'/addStation'" href="#" py-eval="self.localString('Ajouter une station')">
                  </a></td></tr>
                <tr><td align=center><a class=leftHeaderLink py-attr="self.getPath()+'/manageStation'" href="#" py-eval="self.localString('Gerer une station')">
                  </a></td></tr>
                <tr><td colspan=3 py-eval="self.x(190, 1)"></td></tr>
              </table>
            </td></tr>
            <tr><td><br>
              <table border=0 cellspacing=0 cellpadding=0 width=190>
                <tr><th colspan=2 width=190 py-attr="self.color2" bgcolor="" align=center py-eval="self.localString('Partenaire')"></th></tr>
                <tr>
                  <td width=1 py-attr="self.color2" bgcolor="" py-eval="self.x(1)"></td>
                  <td width=189 align=center bgcolor=white>
                    <div py-eval="self.partnerModule()"></div>
                  </td>
                </tr>
                <tr><td colspan=2 width=190 py-eval="self.x(190, 1)"></td></tr>
              </table>
            </td></tr>
            <tr><td><br>
              <table border=0 cellspacing=0 cellpadding=0>
                <tr><th colspan=2 py-attr="self.color2" bgcolor="" align=center py-eval="self.localString('Liens')"></th></tr>
                <tr><td width=1 rowspan=4 py-eval="self.x(1, 200)"></td>
                  <td align=center><a class=leftHeaderLink href="http://stations.gpl.online.fr">
                    GPL Online</a><br><small><small><font color=white>(Site sur les stations GPL)</font></small></small></td></tr>
                <tr><td align=center><a class=leftHeaderLink href="http://www.carburant.org">
                  Carburant.org</a><br><small><small><font color=white>(Site de la baisse de prix du carburant)</font></small></small></td></tr>
                <tr><td align=center><a class=leftHeaderLink href="http://www.jamanga.com">
                  Jamanga.com</a><br><small><small><font color=white>(Le CyberVillage de la route)</font></small></small></td></tr>
                <tr><td align=center><a class=leftHeaderLink href="http://www.argenil.fr.st">
                  Argenil</a><br><small><small><font color=white>(Reduisez vos factures de telephone et les autres)</font></small></small><br></td></tr>
                <tr><td colspan=3 py-eval="self.x(190, 1)"></td></tr>
              </table>
            </td></tr>
          </table>


    def headerMask(self, description, keywords):
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
        <HTML>
        <HEAD>
          <meta http-equiv="robots" content="all">
          <meta name="description" py-attr="description" content="description">
          <meta name="keywords" py-attr="keywords" content="keywords">
          <TITLE py-eval="self.localString('Trouvez la station d\'essence la moins chere pres de chez vous')"></TITLE>
        <div py-if="self==prestationFrench">
            <link rel="stylesheet" py-attr="request.base+'/static/styleSheetFrench.css'" href="#" type="text/css">
        </div><div py-else>
            <link rel="stylesheet" py-attr="request.base+'/static/styleSheetEnglish.css'" href="#" type="text/css">
        </div>
        </HEAD>
        <div py-if="self==prestationFrench">
            <BODY py-attr="request.base+'/static/backgroundFrench.gif'" background="">
        </div><div py-else>
            <BODY py-attr="request.base+'/static/backgroundEnglish.gif'" background="">
        </div>
        <script TYPE="text/javascript">
        function checkFastZipCode(){
           zc=document.fastSearchForm.zipCode.value
           if (isNaN(zc) || zc.length!=5 || zc<'01000' || zc>'95999') {
              alert("<py-eval="self.localString('Le code postal n\'est pas valide')">")
              return false
           }
           document.fastSearchForm.department.value=''
           document.fastSearchForm.keyWord.value=''
           return true
        }
        function checkFastKeyWord() {
           kw=document.fastSearchForm.keyWord.value
           if (kw.length<3) {
              alert("<py-eval="self.localString('Le mot clef doit avoir au moins 3 caracteres')">")
              return false
           }
           document.fastSearchForm.zipCode.value=''
           document.fastSearchForm.department.value=''
           return true
        }
        function checkFastDepartment() {
           id=document.fastSearchForm.department.value
           if (id=='2a' || id=='2A' || id=='2b' || id=='2B') id='20'
           if (id.length==1) id='0'+id
           if (isNaN(id) || id.length!=2 || id<'01' || id>'95') {
              alert("<py-eval="self.localString('Le departement n\'est pas valide')">")
              return false
           }
           document.fastSearchForm.department.value=id
           document.fastSearchForm.zipCode.value=''
           document.fastSearchForm.keyWord.value=''
           return true
        }
        </script>
        
        <table cellspacing=0 width=840>
        <tr>
        <div py-if="self==prestationEnglish">
            <td width=200 class="leftcolumn" valign=top align=left>
                <div py-eval="self.headerColumn()"></div>
            </td>
            <td width=60></td>
        </div>
        <td width=550 valign=top align=center>
            <table width="100%" align=center>
              <tr><td align=center>
                  <div py-if="self==prestationFrench">
                  <img py-attr="request.base+'/static/logoFrench.gif'" src="#">
                  </div><div py-else>
                  <img py-attr="request.base+'/static/logoEnglish.gif'" src="#">
                  </div>
              </td></tr>
              <tr><td align=center width="100%"><br>
              <table width="100%" cellspacing=1 cellpadding=2><tr>
                <td class=topHeaderLink align=center><a class=topHeaderLink py-attr="self.getPath()+'/index'" href="#" py-eval="self.localString('Accueil')"></a></td>
                <td class=topHeaderLink align=center><a class=topHeaderLink py-attr="self.getPath()+'/firstVisit'" href="#" py-eval="self.localString('Premiere visite')"></a></td>
                <td class=topHeaderLink align=center><a class=topHeaderLink py-attr="self.getPath()+'/manager'" href="#" py-eval="self.localString('Vous etes gerant')"></a></td>
                <td class=topHeaderLink align=center><a class=topHeaderLink py-attr="self.getPath()+'/contactUs'" href="#" py-eval="self.localString('Ecrivez-nous')"></a></td>
                <td class=topHeaderLink align=center><a class=topHeaderLink py-attr="self.getPath()+'/wapZone'" href="#" py-eval="self.localString('WAP zone')"></a></td>
             </tr></table></td></tr>
             <tr><td><br><br>

    def partnerModule(self):
        <table border=0 cellpadding=0 cellspacing=0 width=150>
          <tr>
            <td align=center bgcolor=#ffffff><small>
              <a href="http://www.urbishop.com"><img py-attr="request.base+'/static/urbishopLogo.gif'" src="#" border=0></a><br><br>
              <div py-eval="self.localString('Retrouvez les meilleurs offres des magasins pres de chez vous')"></div><br>
              <a class=blackSmallText py-attr="'http://www.urbishop.com'" href="#">UrbiShop.com</a><br><br>
            </small></td>
          </tr>
          <tr>
            <td height=1 align=center bgcolor=white><table border=0 cellspacing=0 cellpadding=0><tr>
              <td height=1 width=90 bgcolor=#aabbdd py-eval="self.x(1, 1)"></td>
            </tr></table></td>
          </tr>
          <tr>
            <td align=left bgcolor=#ffffff class=blackSmallText>
              <form name=partnerForm action="http://www.urbishop.com/dmChangeCity">
              <table border=0 cellspacing=0 cellpadding=0>
                <tr>
                  <td width=5></td>
                  <td width=134 colspan=2 class=blackSmallText><small><br><div py-eval="self.localString('Vous cherchez')"></div>:<br><br></small></td>
                </tr>
                <tr>
                  <td width=5></td>
                  <td class=blackSmallText><small py-eval="self.localString('Quoi')">:</small></td>
                  <td><input type=text name=keyWord size=10 value="portable" onFocus="this.value=''"></td>
                </tr>
                <tr>
                  <td width=5></td>
                  <td class=blackSmallText><small py-eval="self.localString('Ou')"></small></td>
                  <td><input type=text name=city size=10 value="75005" onFocus="this.value=''"></td>
                </tr>
                <tr>
                  <td width=5></td>
                  <td class=blackSmallText><small py-eval="self.localString('Radius')"></small></td>
                  <td><select name=sniffRadius>
                    <div py-for="radius in [0,5,10,30,50,80]">
                      <option py-attr="radius" value="" <div py-if="radius==30">selected</div>>
                      <div py-if="radius!=0"><div py-eval="radius">radius</div> km
                      </div><div py-else>illimite
                      </div>
                      </option>
                    </div>
                  </select></td>
                </tr>
                <tr>
                  <td width=5></td>
                  <td colspan=2 align=center><br><input type=submit py-attr="self.localString('Rechercher')" value=""><br><br></td>
                </tr>
              </table>
              <input type=hidden name=fromPage value="partnerFormPrestation">
              </form>
            </td>
          </tr>
        </table>

    def footer(self):
                </td></tr></table>
            </td>
            <div py-if="self==prestationFrench">
                <td width=60>&nbsp;</td>
                <td width=200 class="leftcolumn" valign=top align=left>
                    <div py-eval="self.headerColumn()"></div>
                </td>
            </div>
            </tr>
            <tr><td align=center>
              <a py-attr="self.getPath()+'/disclaimer'" href="#"><small><small py-eval="self.localString('Mentions legales')"></small></small></a>
            </td></tr>
          </table>
        </body></html>

    def firstVisit(self):
        <div py-eval="self.header()"></div>
        <table width="80%" align=center>
        <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Qu'est-ce que prestation.net ?</small></b></td>
        </tr><tr><td valign=top><small>&nbsp;
        Prestation.net est un site entierement gere par des benevoles dont le but est simple: vous
        permettre de trouver la station d'essence la moins chere pres de l'endroit ou vous vous trouvez.<br>&nbsp;
        Nous disposons d'une base de donnees de stations avec leurs prix. Pour que ces donnees soient
        fiables, nous comptons sur <b>vous</b>, les internautes pour rendre services aux autres en participant.
        Pour cela, vous pouvez relever les prix dans les stations et mettre a jour le site. Vous pouvez
        egalement ajouter de nouvelles stations, ou modifier les coordonnees d'une station.<br>&nbsp;
        De plus, d'autres services sont disponibles ou le seront prochainement comme les
        commentaires sur les stations, plan pour acceder a la station,
        fiches stations detaillees avec photos et ensemble des
        services disponibles dans la station, le portail WAP, etc ...<br><br>
        </small></td></tr>

        <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Comment trouver la station la moins chere pres de chez moi ?</small></b></td>
        </tr><tr><td valign=top><small>&nbsp;
        Le moyen le plus rapide est d'utiliser la recherche rapide disponible dans le menu
        de gauche. Il vous suffit d'entrer votre code postal, ou votre departement. Vous pouvez
        aussi faire une recherche par mot clef ("PARIS" par exemple).<br>&nbsp;
        Si vous voulez faire une recherche plus precise (par exemple, vous voulez un
        type de station bien precis), vous pouvez utiliser la
        <a py-attr="self.getPath()+'/searchStation'" href="#">recherche avancee</a>,
        egalement disponible dans le menu de gauche.<br>&nbsp;
        Lorsque la liste de stations est affichee, vous pouvez la classer par ordre
        de prix du carburant de votre choix. (par defaut, la liste est classee par prix du
        super, du moins cher au plus cher)
        </small></td></tr>
        <tr><td><br><br></td></tr>
        <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Quelles sont les infos disponibles sur les stations ?</small></b></td>
        </tr><tr><td valign=top><small>&nbsp;
        Chaque station est presentee de la facon suivante:<br><br>
        <center><img py-attr="request.base+'/static/stationGraph.gif'" src="#"</center><br>
        </small></td></tr>
        <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Que faire si je vois des informations qui ne sont pas a jour ?</small></b></td>
        </tr><tr><td valign=top><small>&nbsp;
        Vous pouvez mettre a jour un ou plusieurs prix pour une station donnee en cliquant
        sur <b>Mettre a jour les prix</b><br>&nbsp;
        Vous pouvez mettre a jour les informations (par exemple, si le numero de
        telephone change) pour une station donnee en cliquant
        sur <b>Mettre a jour les infos</b><br>&nbsp;
        <u>Pour rendre service aux autres utilisateurs, essayez de mettre a jour les prix
        le plus souvent possible.</u><br><br>
        </small></td></tr>
        <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Pourquoi ce site ?</small></b></td>
        </tr><tr><td valign=top><small>&nbsp;
        Nous sommes un groupe de benevoles ayant constate qu'un site similaire aux
        Etats-unis avait permis a des millions d'Americains de faire des economies.<br>&nbsp;
        Nous avons alors eu l'idee de creer un site similaire en France pour rendre
        service aux consomateurs.
        </small></td></tr>
        </table>
        <div py-eval="self.footer()"></div>

    def disclaimer(self):
        <div py-eval="self.header()"></div>
        <table width="70%" align=center>
        <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Mentions legales</small></b></td>
        </tr><tr><td valign=top><small>&nbsp;
        Le site prestation.net est un site entierement gere par des benevoles, dans le but
        de rendre service aux consommateurs.<br>&nbsp;
        Toutes les informations sur les stations (prix, adresses, horaires, etc ...) sont
        mises a jours par les utilisateurs. L'exactitude de ces informations n'est aucunement
        garantie.<br>&nbsp;
        De meme, les commentaires sur les stations sont donnes par les utilisateurs. Nous n'en
        sommes pas responsables et ils ne reflettent en aucun cas notre avis sur les stations.<br>&nbsp;
        Les noms et logos de marques utilises sur ce site appartiennent aux marques en question.
        Ils sont utilises uniquement afin d'ameliorer la lisibilite et
        la presentation graphique du site.<br>&nbsp;
        Ce site comporte des liens vers d'autres sites. Nous ne sommes absolument pas
        responsable du contenu de ces autres sites.
        </small></td></tr>
        </table>
        <div py-eval="self.footer()"></div>

    def contactUs(self):
        <div py-eval="self.header()"></div>
        <table width="70%" align=center>
        <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Votre avis nous interesse</small></b></td>
        </tr><tr><td valign=top><small>&nbsp;
        - Vous trouvez que l'idee de ce site est geniale ? nulle ?<br>&nbsp;
        - Vous trouvez que le site est bien fait ? pourrait etre nettement mieux ?<br>&nbsp;
        - Vous avez des idees pour ameliorer le site ? Vous aimeriez bien d'autres fonctionalites ?<br>&nbsp;
        <center><b>Faites le nous savoir en envoyant un mail a<br><br>
          <a href="mailto:commentaire@prestation.net">commentaire@prestation.net</a></b></center>
        </small></td></tr>
        <tr><td><br><br></td></tr>
        <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Participez au developpement du site</small></b></td>
        </tr><tr><td valign=top><small>&nbsp;
        - Vous voulez participer au developpement de ce site, que ce soit sur l'aspect programmation,
        graphisme/design ou contenu ?<br>&nbsp;
        - Vous avez bien note que toutes les personnes travaillant sur ce site sont entierement
        benevoles ?<br>&nbsp;
        <center><b>Ecrivez-nous a l'adresse suivante en vous presentant et en nous disant sur quelle partie vous voulez
        travailler<br><br>
          <a href="mailto:participer@prestation.net">participer@prestation.net</a></b></center>
        </small></td></tr>
        </table>
        <div py-eval="self.footer()"></div>

    def manager(self):
        <div py-eval="self.header()"></div>
        <table width="70%" align=center>
        <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Votre etes gerant d'une station</small></b></td>
        </tr><tr><td valign=top><small>&nbsp;
        Si vous etes gerant d'une station dans la vie et que vous aimez internet,
        vous avez la possibilite de "gerer votre station" sur
        notre site.<br>&nbsp;
        Cela signifie que les informations sur votre stations seront bloquees dans
        notre base de donnees et que vous serez le seul a pouvoir changer les prix
        et le reste (grace a un mot de passe).<br>&nbsp;
        De plus, nous vous proposons de creer une fiche individuelle pour votre station
        avec des informations supplementaires et une photo de votre station. Tout cela vous
        est bien sur propose entierement gratuitement.
        Pour en savoir plus, cliquez sur
        <a py-attr="self.getPath()+'/manageStation'" href="#">gerer une station</a>
        dans le menu de gauche ou envoyez nous un mail a<br><br>
        <center><a href="mailto:gerer@prestation.net"><b>gerer@prestation.net</b></a></center>
        </small></td></tr>
        </table>
        <div py-eval="self.footer()"></div>

    def wapZone(self):
        <div py-eval="self.header()"></div>
        <table width="70%" align=center>
        <tr><td colspan=3 align=center py-attr="self.color2" bgcolor=""><b><small>Prestation.net enfin disponible sur le WAP !</small></b></td>
        </tr><tr><td valign=top><img py-attr="request.base+'/static/wap1.jpg'" src="#"><br><br></td><td width=10></td>
        <td><small>&nbsp;
        Si vous possedez un telephone WAP, vous avez desormais la possibilite
        de trouver la station la moins chere <b>ou que vous soyez</b>. Pour cela,
        il vous suffit de vous connecter sur <b>www.prestation.net/wap</b>
        </small></td></tr>
        
        <tr><td colspan=3 align=center py-attr="self.color2" bgcolor=""><b><small>Demonstration du service</small></b></td>
        
        </tr><tr><td valign=top><img py-attr="request.base+'/static/wap2.jpg'" src="#"></td><td width=10></td>
        <td><img py-attr="request.base+'/static/wap3.jpg'" src="#"></td></tr>
        <tr><td colspan=3 align=center><small>&nbsp;
        Sur l'ecran d'accueil, vous choisissez d'abord un code postal ou un
        numero de departement. Puis vous choisissez le type de carburant que
        vous utilisez, puis vous cliquer sur "Lancer la recherche".<br><br>
        </small></td></tr>
        
        <tr><td valign=top><img py-attr="request.base+'/static/wap4.jpg'" src="#"></td><td width=10></td>
        <td><img py-attr="request.base+'/static/wap5.jpg'" src="#"></td></tr>
        <tr><td valign=top><img py-attr="request.base+'/static/wap6.jpg'" src="#"><br><br></td><td width=10></td>
        <td><small>&nbsp;Vous visualisez ensuite les 5 stations les
        moins cheres pour vos criteres. Vous pouvez cliquer sur une station
        pour voir la fiche station.<br><br>
        </small></td></tr>
        
        <tr><td valign=top><img py-attr="request.base+'/static/wap7.jpg'" src="#"></td><td width=10></td>
        <td><img py-attr="request.base+'/static/wap8.jpg'" src="#"></td></tr>
        <tr><td colspan=3 align=center><small>&nbsp;
        Sur la fiche station, vous obtenez l'adresse de la station, le numero
        de telephone, les horaires d'ouverture. Vous obtenez aussi le prix
        des carburants dans cette station, ainsi que la date de la derniere
        mise a jour de ces prix. Vous avez la possibilite de mettre les prix a jour en
        cliquant sur <b>Mettre a jour les prix</b><br><br>
        </small></td></tr>
        
        <tr><td valign=top><img py-attr="request.base+'/static/wap9.jpg'" src="#"></td><td width=10></td>
        <td><img py-attr="request.base+'/static/wap10.jpg'" src="#"></td></tr>
        <tr><td colspan=3 align=center><small>&nbsp;
        Il vous suffit ensuite d'entrer les nouveaux prix et de cliquer sur
        <b>Mettre a jour les prix</b>
        </small></td></tr>

        </table>
        <div py-eval="self.footer()"></div>

##################
CherryClass CheckNew(HttpAuthenticate):
##################
function:
    def __init__(self):
        self.domain="checkNew"
    def getPasswordForLogin(self, login):
        if login==configFile.get('restrictedArea', 'login'): return configFile.get('restrictedArea', 'password')
    def checkNewValidate(self, **kw):
        return self.checkNewAction('validate', kw)
    def checkNewErase(self, **kw):
        return self.checkNewAction('erase', kw)
    def checkNewAction(self, action, kw):
        res='<html><body>'
        requestTable.deleteItem()
        if kw.has_key('newPrice'):
            newPrice=kw['newPrice']
            if type(newPrice)!=types.ListType: newPrice=[newPrice]
            for item in newPrice:
                res+="%s %s<br>"%(action,item)
                if action=='validate': stationTable.updateItem([item.station], super=item.super, sp95=item.sp95, sp98=item.sp98, gazole=item.gazole, lastUpdateTime=item.lastUpdateTime)
                newPriceTable.deleteItem([item])
        if kw.has_key('newInfo'):
            newInfo=kw['newInfo']
            if type(newInfo)!=types.ListType: newInfo=[newInfo]
            for item in newInfo:
                res+="%s %s<br>"%(action,item)
                if action=='validate': stationTable.updateItem([item.station], name=item.name, zipCode=item.zipCode, city=item.city, address=item.address, phone=item.phone, open=item.open, type=item.type, lastUpdateTime=item.lastUpdateTime)
                newInfoTable.deleteItem([item])
        if kw.has_key('newComment'):
            newComment=kw['newComment']
            if type(newComment)!=types.ListType: newComment=[newComment]
            for item in newComment:
                res+="%s %s<br>"%(action,item)
                if action=='validate': commentTable.updateItem([item], checked=1)
                else: commentTable.deleteItem([item])
        if kw.has_key('newStation'):
            newStation=kw['newStation']
            if type(newStation)!=types.ListType: newStation=[newStation]
            for item in newStation:
                res+="%s %s<br>"%(action,item)
                if action=='validate':
                    stationTable.addItem(name=item.name, zipCode=item.zipCode, city=item.city, address=item.address, phone=item.phone, open=item.open, type=item.type, lastUpdateTime=item.lastUpdateTime, super=item.super, sp95=item.sp95, sp98=item.sp98, gazole=item.gazole)
                newStationTable.deleteItem([item])
        res+="</body></html>"
        return res

mask:
    def index(self):
        <html><body>
        <form name=form method=get>
        <center><b>Nouveaux prix</b></center>
        <table align=center border=1>
        <tr><td colspan=2></td>
        <th>stationId</th>
        <th>super</th>
        <th>sp95</th>
        <th>sp98</th>
        <th>gazole</th>
        <th>nom</th>
        <th>date</th>
        <th>Ville, Zip, Nom</th>
        </tr>
        <div py-for="newPrice in newPriceTable.getItem()">
          <tr><td><INPUT TYPE=CHECKBOX name="newPrice" py-attr="newPrice" value='#' checked></td>
          <td>Old<br><b>New</b></td>
          <td py-eval="newPrice.station">station</td>
          <td py-eval="newPrice.station.super">old<br><b py-eval="newPrice.super">super</b></td>
          <td py-eval="newPrice.station.sp95">oldSp95<br><b py-eval="newPrice.sp95">sp95</b></td>
          <td py-eval="newPrice.station.sp98">oldSp98<br><b py-eval="newPrice.sp98">sp98</b></td>
          <td py-eval="newPrice.station.gazole">oldGazole<br><b py-eval="newPrice.gazole">gazole</b></td>
          <td py-eval="newPrice.nameOrEmail">nameOrEmail</td>
          <td py-eval="newPrice.lastUpdateTime">lastUpdate</td>
          <td py-eval="newPrice.station.city+','+newPrice.station.zipCode+','+newPrice.station.name"></td>
        </div>
        </table><br><br>
        <center><b>Nouvelles infos</b></center>
        <table align=center border=1>
        <tr><td colspan=2></td>
        <th>stationId</th>
        <th>nom</th>
        <th>zip</th>
        <th>ville</th>
        <th>adresse</th>
        <th>phone</th>
        <th>ouvert</th>
        <th>type</th>
        <th>nom</th>
        <th>date</th>
        </tr>
        <div py-for="newInfo in newInfoTable.getItem()">
          <tr><td><INPUT TYPE=CHECKBOX name="newInfo" py-attr="newInfo" value='#' checked></td>
          <td>Old<br><b>New</b></td>
          <td py-eval="newInfo.station">station</td>
          <td py-eval="newInfo.station.name+'<br><b>'+newInfo.name+'</b>'"></td>
          <td py-eval="newInfo.station.zipCode+'<br><b>'+newInfo.zipCode+'</b>'"></td>
          <td py-eval="newInfo.station.city+'<br><b>'+newInfo.city+'</b>'"></td>
          <td py-eval="newInfo.station.address+'<br><b>'+newInfo.address+'</b>'"></td>
          <td py-eval="newInfo.station.phone+'<br><b>'+newInfo.phone+'</b>'"></td>
          <td py-eval="newInfo.station.open+'<br><b>'+newInfo.open+'</b>'"></td>
          <td py-eval="newInfo.station.type+'<br><b>'+newInfo.type+'</b>'"></td>
          <td py-eval="newInfo.nameOrEmail">nameOrEmail</td>
          <td py-eval="newInfo.lastUpdateTime">lastUpdate</td>
        </div>
        </table><br><br>
        <center><b>Nouveaux commentaires</b></center>
        <table align=center border=1>
        <tr><td></td>
        <th>stationId</th>
        <th>commentaire</th>
        <th>nom</th>
        <th>date</th>
        <th>Ville, Zip, Nom</th>
        </tr>
        <div py-for="newComment in commentTable.getItem('item.checked==0')">
          <tr><td><INPUT TYPE=CHECKBOX name="newComment" py-attr="newComment" value='#' checked></td>
          <td py-eval="newComment.station"></td>
          <td py-eval="newComment.comment"></td>
          <td py-eval="newComment.nameOrEmail"></td>
          <td py-eval="newComment.lastUpdateTime"></td>
          <td py-eval="newComment.station.city+','+newComment.station.zipCode+','+newComment.station.name"></td>
        </div>
        </table><br><br>
        <center><b>Nouvelles stations</b></center>
        <table align=center border=1>
        <tr><td></td>
        <th>nom</th>
        <th>zip</th>
        <th>ville</th>
        <th>adresse</th>
        <th>phone</th>
        <th>ouvert</th>
        <th>type</th>
        <th>super</th>
        <th>sp95</th>
        <th>sp98</th>
        <th>gazole</th>
        <th>nom</th>
        <th>date</th>
        </tr>
        <div py-for="newStation in newStationTable.getItem()">
          <tr><td><INPUT TYPE=CHECKBOX name="newStation" py-attr="newStation" value='#' checked></td>
          <td py-eval="newStation.name"></td>
          <td py-eval="newStation.zipCode"></td>
          <td py-eval="newStation.city"></td>
          <td py-eval="newStation.address"></td>
          <td py-eval="newStation.phone"></td>
          <td py-eval="newStation.open"></td>
          <td py-eval="newStation.type"></td>
          <td py-eval="newStation.super"></td>
          <td py-eval="newStation.sp95"></td>
          <td py-eval="newStation.sp98"></td>
          <td py-eval="newStation.gazole"></td>
          <td py-eval="newStation.nameOrEmail"></td>
          <td py-eval="newStation.lastUpdateTime"></td>
        </div>
        </table>
        <br><br>

        <center><b>Nouvelles requetes</b></center>
        <table align=center border=1>
        <tr>
        <th>Requete</th>
        <th>Date</th>
        </tr>
        <div py-for="myRequest in requestTable.getItem()">
          <tr>
          <td py-eval="myRequest.name"></td>
          <td py-eval="myRequest.lastUpdateTime"></td>
        </div>
        </table>
        <br><br>

        <center><input type=submit value="Valider les infos"
          onClick="javascript:document.form.action='<div py-eval="self.getPath()+'/checkNew/checkNewValidate'"></div>'">&nbsp;&nbsp;
        <input type=submit value="Effacer les infos"
          onClick="javascript:document.form.action='<div py-eval="self.getPath()+'/checkNew/checkNewErase'"></div>'">&nbsp;&nbsp;
        </form>
        </body></html>


##################
CherryClass PrestationMail(Mail):
##################
function:
    def __init__(self):
        self.smtpServer=configFile.get('mail', 'mailServer')
