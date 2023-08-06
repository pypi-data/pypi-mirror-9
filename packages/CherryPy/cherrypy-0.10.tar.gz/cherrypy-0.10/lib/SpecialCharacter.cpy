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
CherryClass SpecialCharacter:
################
variable:
    # List of special characters: [entity, decimal, hex, rendering]
    specialCharacterList=[
        ("&nbsp;","&#160;","&#xA0;"," "),
        ("&iexcl;","&#161;","&#xA1;","¡"),
        ("&cent;","&#162;","&#xA2;","¢"),
        ("&pound;","&#163;","&#xA3;","£"),
        ("&curren;","&#164;","&#xA4;","¤"),
        ("&yen;","&#165;","&#xA5;","¥"),
        ("&brvbar;","&#166;","&#xA6;","¦"),
        ("&sect;","&#167;","&#xA7;","§"),
        ("&uml;","&#168;","&#xA8;","¨"),
        ("&copy;","&#169;","&#xA9;","©"),
        ("&ordf;","&#170;","&#xAA;","ª"),
        ("&laquo;","&#171;","&#xAB;","""),
        ("&not;","&#172;","&#xAC;",""),
        ("&reg;","&#174;","&#xAE;","®"),
        ("&macr;","&#175;","&#xAF;","¯"),
        ("&deg;","&#176;","&#xB0;","°"),
        ("&plusmn;","&#177;","&#xB1;","±"),
        ("&sup2;","&#178;","&#xB2;","²"),
        ("&sup3;","&#179;","&#xB3;","³"),
        ("&acute;","&#180;","&#xB4;","´"),
        ("&micro;","&#181;","&#xB5;","µ"),
        ("&para;","&#182;","&#xB6;",""),
        ("&middot;","&#183;","&#xB7;","·"),
        ("&cedil;","&#184;","&#xB8;","¸"),
        ("&sup1;","&#185;","&#xB9;","¹"),
        ("&ordm;","&#186;","&#xBA;","º"),
        ("&raquo;","&#187;","&#xBB;","""),
        ("&frac14;","&#188;","&#xBC;","¼"),
        ("&frac12;","&#189;","&#xBD;","½"),
        ("&frac34;","&#190;","&#xBE;","¾"),
        ("&iquest;","&#191;","&#xBF;","¿"),
        ("&Agrave;","&#192;","&#xC0;","À"),
        ("&Aacute;","&#193;","&#xC1;","Á"),
        ("&Acirc;","&#194;","&#xC2;","Â"),
        ("&Atilde;","&#195;","&#xC3;","Ã"),
        ("&Auml;","&#196;","&#xC4;","Ä"),
        ("&Aring;","&#197;","&#xC5;","Å"),
        ("&AElig;","&#198;","&#xC6;","Æ"),
        ("&Ccedil;","&#199;","&#xC7;","Ç"),
        ("&Egrave;","&#200;","&#xC8;","È"),
        ("&Eacute;","&#201;","&#xC9;","É"),
        ("&Ecirc;","&#202;","&#xCA;","Ê"),
        ("&Euml;","&#203;","&#xCB;","Ë"),
        ("&Igrave;","&#204;","&#xCC;","Ì"),
        ("&Iacute;","&#205;","&#xCD;","Í"),
        ("&Icirc;","&#206;","&#xCE;","Î"),
        ("&Iuml;","&#207;","&#xCF;","Ï"),
        ("&ETH;","&#208;","&#xD0;","Ð"),
        ("&Ntilde;","&#209;","&#xD1;","Ñ"),
        ("&Ograve;","&#210;","&#xD2;","Ò"),
        ("&Oacute;","&#211;","&#xD3;","Ó"),
        ("&Ocirc;","&#212;","&#xD4;","Ô"),
        ("&Otilde;","&#213;","&#xD5;","Õ"),
        ("&Ouml;","&#214;","&#xD6;","Ö"),
        ("&times;","&#215;","&#xD7;","×"),
        ("&Oslash;","&#216;","&#xD8;","Ø"),
        ("&Ugrave;","&#217;","&#xD9;","Ù"),
        ("&Uacute;","&#218;","&#xDA;","Ú"),
        ("&Ucirc;","&#219;","&#xDB;","Û"),
        ("&Uuml;","&#220;","&#xDC;","Ü"),
        ("&Yacute;","&#221;","&#xDD;","Ý"),
        ("&THORN;","&#222;","&#xDE;","Þ"),
        ("&szlig;","&#223;","&#xDF;","ß"),
        ("&agrave;","&#224;","&#xE0;","à"),
        ("&aacute;","&#225;","&#xE1;","á"),
        ("&acirc;","&#226;","&#xE2;","â"),
        ("&atilde;","&#227;","&#xE3;","ã"),
        ("&auml;","&#228;","&#xE4;","ä"),
        ("&aring;","&#229;","&#xE5;","å"),
        ("&aelig;","&#230;","&#xE6;","æ"),
        ("&ccedil;","&#231;","&#xE7;","ç"),
        ("&egrave;","&#232;","&#xE8;","è"),
        ("&eacute;","&#233;","&#xE9;","é"),
        ("&ecirc;","&#234;","&#xEA;","ê"),
        ("&euml;","&#235;","&#xEB;","ë"),
        ("&igrave;","&#236;","&#xEC;","ì"),
        ("&iacute;","&#237;","&#xED;","í"),
        ("&icirc;","&#238;","&#xEE;","î"),
        ("&iuml;","&#239;","&#xEF;","ï"),
        ("&eth;","&#240;","&#xF0;","ð"),
        ("&ntilde;","&#241;","&#xF1;","ñ"),
        ("&ograve;","&#242;","&#xF2;","ò"),
        ("&oacute;","&#243;","&#xF3;","ó"),
        ("&ocirc;","&#244;","&#xF4;","ô"),
        ("&otilde;","&#245;","&#xF5;","õ"),
        ("&ouml;","&#246;","&#xF6;","ö"),
        ("&divide;","&#247;","&#xF7;","÷"),
        ("&oslash;","&#248;","&#xF8;","ø"),
        ("&ugrave;","&#249;","&#xF9;","ù"),
        ("&uacute;","&#250;","&#xFA;","ú"),
        ("&ucirc;","&#251;","&#xFB;","û"),
        ("&uuml;","&#252;","&#xFC;","ü"),
        ("&yacute;","&#253;","&#xFD;","ý"),
        ("&thorn;","&#254;","&#xFE;","þ"),
        ("&yuml;","&#255;","&#xFF;","ÿ")
    ]
    #"&shy;","&#173;","&#xAD;","",

function:
    def toRendering(self, text):
        for entity, decimal, hex, rendering in self.specialCharacterList:
            text=text.replace(entity, rendering)
            text=text.replace(decimal, rendering).replace('\\'+decimal[2:-1], rendering)
            text=text.replace(hex, rendering).replace('\\'+hex[2:-1], rendering).replace('\\'+hex[2:-1].lower(), rendering)
        return text

