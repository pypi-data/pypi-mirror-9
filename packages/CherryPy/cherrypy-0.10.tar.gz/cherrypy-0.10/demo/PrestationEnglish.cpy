use Prestation

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
CherryClass PrestationEnglish(Prestation):
################
variable:
    stringMap={
        "Prestation.net - Mentions legales": "Prestation.net - Disclaimer",
        "loi, essence": "law, gas",
        "Prestation.net - Wap": "Prestation.net - Wap",
        "wap, prix": "wap, price",
        "Prestation.net - Contactez nous": "Prestation.net - Contact us",
        "contact, mail": "contact, mail",
        "Prestation.net - Devenir gerant": "Prestation.net - Become a manager",
        "gerer, gerant": "manager",
        "Prestation.net - Premiere visite": "Prestation.net - First visit",
        "premier, visite": "first, visite",
        "Prestation.net - Gerer une station": "Prestation.net - Manage a gas station",
        "gerer, station": "manage, station",
        "Prestation.net - Ajouter une station": "Prestation.net - Add a new gas station",
        "ajouter, station": "add, station",
        "Prestation.net - Chercher une station": "Prestation.net - Find a gas station",
        "chercher, recherche": "find, search",
        "Trouvez la station d'essence la moins chere pres de chez vous": "Find the cheapest gas station near you",
        "essence, super, gasole, gazoil, sans plomb, 95, 98, prix, carburant, pompe, station, pas cher, pas chere": "gas, price, station",
        "Votre demande a ete envoyee": "Your request has been sent",
        "Nous vous contacterons d'ici 24 a 72 heures": "We will contact you within 24 hours",
        "Nom": "Name",
        "Email": "Email:",
        "Station": "Gas station",
        "Stations": "Gas stations",
        "Raison": "Reason",
        "Autre raison": "Other reason",
        "Mot de passe": "Password",
        "Vous devez entrer vos commentaires": "You must enter your comment",
        "Entrez vos commentaires sur la station": "Please enter your comment on the gas station",
        "Commentaire": "Comment",
        "Votre nom ou e-mail (facultatif)": "Your name or e-mail (optional)",
        "Valider": "OK",
        "Annuler": "Cancel",
        "Le code postal n'est pas valide": "Non valid zipCode",
        "Le mot clef doit avoir au moins 3 caracteres": "Keyword is not long enough",
        "Le departement n'est pas valide": "Non valid department code",
        "Recherche rapide": "Fast search",
        "Code postal": "Zip code",
        "Departement": "Department",
        "Mot clef": "Keyword",
        "Partenaire": "Partner",
        "Liens": "Links",
        "Accueil": "Home",
        "Premiere visite": "First visit",
        "Vous etes gerant": "Manager zone",
        "Ecrivez-nous": "Contact us",
        "Recherche avancee": "Advanced search",
        "Ajouter une station": "Add a new station",
        "Gerer une station": "Manage a station",
        "Retrouvez les meilleurs offres des magasins pres de chez vous": "Find the best deals in stores near you",
        "Vous cherchez": "You want",
        "Quoi": "What",
        "Ou": "Where",
        "Rayon": "Radius",
        "Rechercher": "Find",
        "Mentions legales": "Disclaimer",
    }

    color1="#0060CE"
    color2="#BDCEDE"

function:
    # Return the date in England using English format
    def getDate(self):
        tuple=time.gmtime(time.time())
        res=time.strftime("%Y/%m/%d", tuple)
        return res

    # Format a date to display it
    def formatDateForDay(self, date):
        year=date[:4]
        month=date[5:7]
        day=date[8:10]
        return year+'/'+month+'/'+day

    # Return the tag for a go image
    def go(self):
        return '<img src="%s/static/goEnglish.gif" border=0 align=absmiddle>'%request.base

mask:
    def noStation(self):
        <div py-eval="self.header()"></div>
          <center><B>No gas station was found for these criteria</b><br><br>
            Try using less restrictive criteria<br><br>
            <form><input type=button value=Back onClick="javascript:history.back()"></form>
          </center>
        <div py-eval="self.footer()"></div>

    def tooManyStation(self):
        <div py-eval="self.header()"></div>
          <center><h3>
            More than 50 gas stations match these criteria</h3>
            Please narrow your search
            <br><br>
            <form><input type=button value=Back onClick="javascript:history.back()"></form>
          </center>
        <div py-eval="self.footer()"></div>


    def index(self):
        <div py-eval="self.header()"></div>
        <table width="100%" align=center><tr>
        <td width="50%" align=center py-attr="self.color2" bgcolor=""><b><small>Welcome</small></b></td>
        <td width=10></td>
        <td align=center py-attr="self.color2" bgcolor=""><b><small>Update prices</small></b></td>
        </tr><tr><td valign=top align=left><small>&nbsp;
        Prestation.net's goal is to allow consumers to find the cheapest gas station near them.<br>
        &nbsp;This website is a non-profit website based on a community spirit.
        Users help each other by updating prices for gas stations.<br>
        &nbsp;Several services are already available. Among them are comments, maps, wap, ...
        Other services are coming up soon. Among them are gas stations photos, opening hours and available
        services.
        </small></td>
        <td width=10></td>
        <td valign=top align=left><small>&nbsp;
          This website is a non-profit website, and we're counting on <b>you</b>
          to help other users by updating gas prices.<br>
          &nbsp;<u>For some regions, the prices are only rarely updated. But we are counting
          on your help to change that.</u><br>
          </small><br>
          <table width=100%>
            <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Tell us what you think</small></b></td></tr>
            <tr><td valign=top align=left><small>&nbsp;
              For each gas station, you can post messages to let other people know what you think
              about this station. Who knows, maybe the manager of the station will hear you ...
            </small></td></tr>
          </table>
        </td></tr></table>
        <br>
        <table><tr>
        <td colspan=3 align=center py-attr="self.color2" bgcolor=""><b><small>English version's not finished yet</small></b></td>
        </tr><tr><td colspan=3 valign=top align=left><small>&nbsp;
        As you will notice, some parts of the website haven't been translated into English yet.
        We'll try to do it when we have time.
        <br><br>
        </small></td>
        </tr></table>

        
        <div py-eval="self.footer()"></div>

