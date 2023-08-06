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
# As a special exception, the CherryPy Team gives unlimited permission to 
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
# released by Remi Delon and contributors.  When you make and distribute a modified 
# version of CherryPy, you may extend this special exception to the 
# GPL to apply to your modified version as well, *unless* your 
# modified version has the potential to copy into its output some of 
# the text that was the non-data portion of the version that you 
# started with.  (In other words, unless your change moves or copies 
# text from the non-data portions to the data portions.)  If your 
# modification has such potential, you must delete any notice of this 
# special exception to the GPL from your modified version. 

  

README for CherryPy
------------------------------
To get more information about CherryPy, go to http://www.cherrypy.org

* To run the demo, go to demo/ and type:

    python ../cherrypy.py Root.cpy

(python must be version 2.1 or higher)

This will create a file called RootServer.py
Then, just run it by typing:

    python RootServer.py

Open a browser, enter http://localhost:8000/ in the URL, and voila


* To run the regression test suite, go to test/ and type:

    python testCherryPy.py

    (if Python is installed in an unusual place on your system, edit testCherry.py and specify the path to your
    python binarie(s) at the beginning of the file)


* To run the www.cherrypy.org site (without the forum) on your local machine, go to www.cherrypy.org/ and type:

    python ../cherrypy.py -I ../demo CherryPy.cpy Demo.cpy PrestationFrench.cpy PrestationEnglish.cpy
    python CherryPyServer.py


* If you're just getting started with CherryPy, read the tutorial (in doc/html/tut/index.html)

