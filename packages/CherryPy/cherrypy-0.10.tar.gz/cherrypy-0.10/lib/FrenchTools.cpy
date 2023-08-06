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

import types, smtplib

################
CherryClass FrenchTools:
################
function:
    # Some functions to manipulate french dates (probably usefull only to me :-))
    def getDate(self, withYear=0, withBr=0):
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
        if withBr: br="<br>"
        else: br=" "
        res="%s%s%s %s"%(dayMap[dayOfWeekNb], br, dayNb, monthMap[monthNb])
        if withYear: res+="%s2002"%br
        return res
    def formatDateForDay(self, date):
        year=date[:4]
        month=date[5:7]
        day=date[8:10]
        return day+'/'+month+'/'+year
    def getNow(self):
        # Return a string in the MySql format with the local time in France
        tuple=time.gmtime(time.time()+3600) # Local time in France
        return time.strftime('%Y-%m-%d %H:%M:%S', tuple)
    def getNowMinus(self, day):
        tuple=time.gmtime(time.time()+3600-(3600*24*day)) # Local time in France minus n days
        return time.strftime('%Y-%m-%d %H:%M:%S', tuple)
    def validateBirthDate(self, birthDate, sep='/'):
        try:
            day, month, year=birthDate.split('/')
            if int(day)<1 or int(day)>31: raise "Error"
            if int(month)<1 or int(month)>12: raise "Error"
            if int(year)<1890 or int(year)>2000: raise "Error"
        except: return "Wrong birthDate"

    def validateZipCode(self, zipCode):
        try:
            if int(zipCode)<01000 or int(zipCode)>98999: raise 'Error'
        except: return "Wrong zipCode"

    def strToFloat(self, num):
        if not num: return 0
        if type(num)==type(''): num=num.replace(',','.')
        return float(num)

    def floatToStr(self, num):
        if not num: return ''
        return str(num).replace('.',',')
