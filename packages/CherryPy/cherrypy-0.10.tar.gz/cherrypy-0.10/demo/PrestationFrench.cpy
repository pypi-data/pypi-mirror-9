use Prestation


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


################
CherryClass PrestationFrench(Prestation):
################
variable:
    color1="#FF4040"
    color2="#FF9900"

function:
    # Return the date in France using French format
    def getDate(self):
        dayMap={
            '0': 'dimanche',
            '1': 'lundi',
            '2': 'mardi',
            '3': 'mercredi',
            '4': 'jeudi',
            '5': 'vendredi',
            '6': 'samedi'
        }
        monthMap={
            '01': 'janvier',
            '02': 'fevrier',
            '03': 'mars',
            '04': 'avril',
            '05': 'mai',
            '06': 'juin',
            '07': 'juillet',
            '08': 'aout',
            '09': 'septembre',
            '10': 'octobre',
            '11': 'novembre',
            '12': 'decembre'
        }
        tuple=time.gmtime(time.time()+3600) # Local time in France
        dayOfWeekNb=time.strftime("%w", tuple)
        monthNb=time.strftime("%m", tuple)
        dayNb=int(time.strftime("%d", tuple))
        res="%s %s %s"%(dayMap[dayOfWeekNb], dayNb, monthMap[monthNb])
        return res

    # Format a date to display it
    def formatDateForDay(self, date):
        year=date[:4]
        month=date[5:7]
        day=date[8:10]
        return day+'/'+month+'/'+year


    # Return the tag for a go image
    def go(self):
        return '<img src="%s/static/goFrench.gif" border=0 align=absmiddle>'%request.base

mask:
    def noStation(self):
        <div py-eval="self.header()"></div>
          <center><B>Aucune station n'a ete trouvee pour ces criteres</b><br><br>
            Essayez d'elargir vos criteres de recherche<br><br>
            <form><input type=button value=Retour onClick="javascript:history.back()"></form>
          </center>
        <div py-eval="self.footer()"></div>

    def tooManyStation(self):
        <div py-eval="self.header()"></div>
          <center><h3>
            Plus de 50 stations correspondent a ces criteres</h3>
            Vous devez preciser votre recherche
            <br><br>
            <form><input type=button value=Retour onClick="javascript:history.back()"></form>
          </center>
        <div py-eval="self.footer()"></div>


    def index(self):
        <div py-eval="self.header()"></div>
        <table width="100%" align=center><tr>
        <td width="50%" align=center py-attr="self.color2" bgcolor=""><b><small>Bienvenue</small></b></td>
        <td width=10></td>
        <td align=center py-attr="self.color2" bgcolor=""><b><small>Mettez les prix a jour</small></b></td>
        </tr><tr><td valign=top align=left><small>&nbsp;
        Prestation.net a pour but de permettre aux consommateurs de trouver
        la station d'essence la moins chere pres de chez eux.<br>
        &nbsp;Le site est
        gere entierement par des benevoles, dans un esprit communautaire.
        Ce sont les internautes eux-memes qui se rendent service
        mutuellement en venant mettre a jour les prix des stations.<br>
        &nbsp;Plusieurs services sont disponibles, comme les commentaires sur
        les stations, les plans d'acces aux stations, le portail WAP, et
        d'autres services sont en preparation, comme la presentation
        detaillee des stations services avec photos, horaires d'ouverture,
        services disponibles, etc ...
        </small></td>
        <td width=10></td>
        <td valign=top align=left><small>&nbsp;
          Ce site est gere entierement par des benevoles, et nous comptons sur
          <b>vous</b> pour rendre service aux autres utilisateurs en mettant les prix
          a jour.<br>&nbsp;
          <u>Certaines regions ne sont que rarement mises a jour, mais nous
          comptons sur votre aide pour changer cela.</u><br>
          </small><br>
          <table width=100%>
            <tr><td align=center py-attr="self.color2" bgcolor=""><b><small>Donnez votre avis</small></b></td></tr>
            <tr><td valign=top align=left><small>&nbsp;
              Chaque station possede son mini forum ou vous pouvez donner votre avis ou faire
              partager vos remarques sur cette station. Tous les internautes (y compris les
              gerants de la stations) peuvent alors lire vos commentaires.
            </small></td></tr>
          </table>
        </td></tr></table>
        <br>
        
        
        <table><tr>
        <td colspan=3 align=center py-attr="self.color2" bgcolor=""><b><small>Il y a du nouveau sur prestation.net</small></b></td>
        </tr><tr><td colspan=3 valign=top align=left><small>&nbsp;
        Tout d'abord, nous tenons a remercier toutes les personnes qui viennent
        mettre a jour les prix ou qui ajoutent de nouvelles stations. Meme si
        nous sommes encore loin d'avoir tous les prix de toutes les stations
        regulierement a jour, nous avons certaines regions ou les informations
        que vous nous envoyez sont suffisament nombreuses et regulieres pour
        etre pertinentes.<br>&nbsp;
        Plusieurs personnes se sont egalement portees volontaires pour "gerer"
        une station sur le site. Merci beaucoup.<br>&nbsp;
        Nous avons decide de creer une nouvelle rubrique intitulee <b>Station
        de la semaine</b>. Le principe est simple: chaque semaine, nous
        presenterons en page d'accueil une station avec photo, services,
        presentation du personnel, etc...  (messieurs les gerants, contactez
        nous si vous souhaitez voir votre station sur notre site - ce service
        est bien sur entierement gratuit).<br>&nbsp;
        Vous avez ete nombreux a nous feliciter et nous encourager pour ce
        site. <b>Merci
        pour votre soutien.</b> Nous allons prochainement publier quelques-uns des
        mails de felicitations que nous avons recus.
        <br><br>
        </small></td>
        </tr></table>
        <div py-eval="self.footer()"></div>

