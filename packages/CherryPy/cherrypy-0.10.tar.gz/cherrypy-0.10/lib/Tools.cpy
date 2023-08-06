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

import types, smtplib, time

################
CherryClass Tools:
################
variable:
    # Some constants that are quite handy to use within special tags in "mask" functions
    quote="'"
    doubleQuote="'"

function:

    # Function to "compress" a html body
    # This can save a few kilos of every page
    # Basically, all extra spaces and newlines are removed
    # Code between <script and </script>, or <textarea> and </textarea> (lowercase or uppercase) is preserved
    def compressHtml(self, body):
        i=body.find('<script')
        if i!=-1:
            j=body.find('</script>', i)
            return self.compressHtml(body[:i])+'\n'+body[i:j+9]+'\n'+self.compressHtml(body[j+9:])
        i=body.find('<SCRIPT')
        if i!=-1:
            j=body.find('</SCRIPT>', i)
            return self.compressHtml(body[:i])+'\n'+body[i:j+9]+'\n'+self.compressHtml(body[j+9:])
        i=body.find('<textarea')
        if i!=-1:
            j=body.find('</textarea>', i)
            return self.compressHtml(body[:i])+'\n'+body[i:j+11]+'\n'+self.compressHtml(body[j+11:])
        i=body.find('<TEXTAREA')
        if i!=-1:
            j=body.find('</TEXTAREA>', i)
            return self.compressHtml(body[:i])+'\n'+body[i:j+11]+'\n'+self.compressHtml(body[j+11:])
        return string.join(body.split())

    def getAttribute(self, attributeName, attributeValue):
        if attributeValue: return attributeName+'='+`attributeValue`
        return ""

    def validateEmail(self, email):
        try:
            before, after=email.split('@')
            if not before or after.find('.')==-1: raise 'Error'
        except: return "Wrong email"

    def getLabelWithCount(self, count, label, pluralLabel):
        if count<=1: return "%s %s"%(count, label)
        else: return "%s %s"%(count, pluralLabel)

    def getNow(self):
        # Return a string in the MySql format
        tuple=time.gmtime(time.time()) # Local time
        return time.strftime('%Y-%m-%d %H:%M:%S', tuple)

    def escapeHtml(self, data, newlineToBr=1, whitespaceToNbsp=1, tabTo4ws=1):
        entityMap=[
            ('&','&amp;'),
            ('<','&lt;'),
            ('>','&gt;'),
            ('"','&quot;')]
        for k,v in entityMap: data=data.replace(k,v)
        if newlineToBr: data=data.replace('\n','<br>')
        if whitespaceToNbsp: data=data.replace('  ','&nbsp;&nbsp;')
        if tabTo4ws: data=data.replace('\t', '&nbsp;'*4)
        return data
