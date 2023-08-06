#!/usr/bin/env python
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

import string, sys, getopt, os

import re
reValidClassName = re.compile('^[A-Z][a-zA-Z0-9_\.]*$')

version="0.10"

quote3='\"\"\"'

specialFunctionList = ['initRequestBeforeParse()', 'initRequest()', 'initNonStaticRequest()', 'initResponse()', 'initNonStaticResponse()',
    'initServer()', 'initProgram()', 'initThread(threadIndex)', 'initProcess(processIndex)', 'initAfterBind()',
    'hotReloadInitServer()', 'onError()', 'logMessage(message, level=0)', 'saveSessionData(sessionId, sessionData, expirationTime)',
    'loadSessionData(sessionId)', 'cleanUpOldSessions()']

class emptyClass:
    pass

def getNextLine(lines, lineIndex):
    while 1:
        try: line=lines[lineIndex]
        except IndexError: return "", lineIndex
        lineIndex+=1
        if line and line.split() and line.split()[0][0]!='#': return line.rstrip(), lineIndex
        if lineIndex==len(lines): return '', lineIndex

def lowerFirst(str):
    return str[0].lower()+str[1:]

def parseSpecialFunction(lines, lineIndex):
    result=""
    while 1:
        line, lineIndex=getNextLine(lines, lineIndex)
        sp=line.split('    ')
        if sp[0] or not line:
            if line: lineIndex-=1
            break
        result+=line+'\n'
    return result, lineIndex

def raiseError(msg, withLine=1, withCherryClass=0, withFunction=0):
    error="CherryError: "+msg+"\n    in File %s"%`parserPos.fileName`
    if withLine:
        error+=", line %s"%parserPos.lineIndex
    if withCherryClass:
        error+=", in CherryClass '%s'"%parserPos.cherryClassName
    if withFunction:
        error+=", in function '%s'"%parserPos.maskName
    raise error

def parseModule(parsedModule, moduleName):
    lines=getModuleLines(parsedModule.includeDirList, moduleName, '.cpy')
    while lines:
        if lines[0][:4]=='use ': lines=lines[1:]
        else: break

    if moduleName.find('.cpy')==-1: parserPos.fileName=moduleName+'.cpy'
    else: parserPos.filename=moduleName

    lineIndex=0
    while 1:
        line, lineIndex=getNextLine(lines, lineIndex)
        parserPos.lineIndex=lineIndex
        if not line: break
        # If line starts with debug and debug is not turned on, ignore line
        if not _debug and line.split()[0][:6]=='debug(': continue
        sp=line.split('    ')

        isSpecialFunction = 0
        for specialFunction in specialFunctionList:
            l = len(specialFunction)
            if line[:l+5] == 'def %s:' % specialFunction:
                i = specialFunction.find('(')
                specialFunctionBody, lineIndex=parseSpecialFunction(lines, lineIndex)
                exec('parsedModule.%s += specialFunctionBody' % specialFunction[:i])
                isSpecialFunction = 1

        if line[:6]=='import':
            parsedModule.importList.append(line)
        elif line[:5]=='from ' and line.find(' import ')!=-1:
            parsedModule.importList.append(line)

        elif line[:12]=='CherryClass ':        # cat 0 : CherryClass
            if line[-1] != ':': raiseError("CherryClass declaration line doesn't end with ':'")
            cat1=""
            sp2=line[:-1].split()[1:]
            if sp2[-1]=='abstract':
                sp2=sp2[:-1]
                abstract=1
            else: abstract=0
            if sp2[-1]=='hidden':
                sp2=sp2[:-1]
                hidden=1
            else:
                hidden=0
            if sp2[-1]=='xmlrpc':
                sp2=sp2[:-1]
                xmlrpc=1
            else:
                xmlrpc=0
            cherryClass=string.join(sp2).replace(' ','')

            # Identify CherryClass name and parent names
            parentList=[]
            i=cherryClass.find('(')
            if i!=-1:
                if cherryClass[-1]!=')': raiseError("CherryClass declaration doesn't end with ')'")
                parentList=cherryClass[i+1:-1].split(',')
                cherryClass=cherryClass[:i]
            parsedModule.parentListMap[cherryClass] = parentList
            
            # Check that cherryClass name starts with an upper case letter and
            # fits Python type naming schemes
            if not reValidClassName.match(cherryClass):
                raiseError("CherryClass '%s' name is invalid.  Name must start with an upper case character and consist only of letters, numbers and underscores." % cherryClass)

            if abstract: parsedModule.abstractClassList.append(cherryClass)
            if hidden: parsedModule.hiddenClassList.append(cherryClass)
            if xmlrpc: parsedModule.xmlrpcClassList.append(cherryClass)

            currentMap={}
            parsedModule.cherryClassList.append((cherryClass,currentMap,parserPos.fileName))

        elif sp[0]=="variable:" or sp[0]=="function:" or sp[0]=="view:" or sp[0]=="mask:" or sp[0]=="aspect:":    # cat 1 : function, view, mask or aspect
            cat1=sp[0][:-1]

        elif len(sp)>1 and sp[1]:            # cat 2
            if not cat1:
                raiseError('Line should be inside a section')
            if cat1=="variable" or cat1=='function' or cat1=='view' or cat1=='mask': # list of variables or functions
                currentBody=""
                while 1:
                    line=string.join(sp[1:],'    ')
                    currentBody+=line+'\n'
                    line, lineIndex=getNextLine(lines, lineIndex)
                    sp=line.split('    ')
                    if cat1 in ['function', 'view', 'mask'] and len(sp)>1 and not sp[0] and sp[1] and sp[1][:4]!='def ':
                        raiseError("Not a valid line: '%s'"%line)
                    if sp[0] or not line:
                        if not currentMap.has_key(cat1): currentMap[cat1] = currentBody[:-1]
                        else: currentMap[cat1] += '\n' + currentBody[:-1]
                        # print "currentMap[%s]: %s" % (cat1, repr(currentMap[cat1]))
                        if line: lineIndex-=1
                        break
            elif cat1=='aspect': # list of functions
                currentAspectMap={'start': [], 'end': []}
                parsedModule.aspectMap[cherryClass]=currentAspectMap
                isFirst=1
                while 1:
                    if sp[1]: # Aspect define
                        if not isFirst: currentAspectMap[startOrEnd].append((applyTo, currentBody))
                        aspectHeader=sp[1][:-1].split()
                        startOrEnd=aspectHeader[-1]
                        if startOrEnd not in ("start","end"):
                            raiseError("Wrong aspect header: '%s'"%sp[1])
                        applyTo=string.join(aspectHeader[:-1])
                        currentBody=""
                    else:
                        line=string.join(sp[2:],'    ')
                        currentBody+=line+'\n'
                        isFirst=0
                    line, lineIndex=getNextLine(lines, lineIndex)
                    sp=line.split('    ')
                    if sp[0] or not line:
                        currentAspectMap[startOrEnd].append((applyTo,currentBody))
                        if line: lineIndex-=1
                        break
            else: raiseError("Not a valid section: '%s'"%cat1)

        elif not isSpecialFunction: raiseError("Not a valid line: '%s'"%line)

def writeCherryClass(f, parsedModule):
    for cherryClass, currentMap, fileName in parsedModule.cherryClassList:
        # print "Writing cherryClass:",cherryClass
        parserPos.fileName=fileName
        parserPos.cherryClassName=cherryClass
        cherryClassInstance=lowerFirst(cherryClass)
        parentList = parsedModule.parentListMap[cherryClass]
    
        # Declare class for cherryClass
        if _debug: f.write('global %s\n'%cherryClass)
        if parentList: f.write('class %s(%s):\n'%(cherryClass, string.join(parentList,',')))
        else: f.write('class %s:\n'%cherryClass)

        # Write variables if any
        if currentMap.has_key('variable') and currentMap['variable']:
            for line in currentMap['variable'].split('\n'):
                f.write('    '+line+'\n')


        # Write special getPath function
        f.write('    def getPath(self, includeRequestBase = 1):\n')
        f.write('        if includeRequestBase:\n')
        f.write('            return request.base + "/%s"\n'%cherryClassInstance.replace('_','/'))
        f.write('        else:\n')
        f.write('            return "/%s"\n'%cherryClassInstance.replace('_','/'))
        writeFunction(f, cherryClass, parsedModule, currentMap, 'function')
        writeFunction(f, cherryClass, parsedModule, currentMap, 'view')
        writeFunction(f, cherryClass, parsedModule, currentMap, 'mask')
        # Instantiate CherryClass
        i=cherryClass.find('(')
        if i!=-1:
            cherryClass=cherryClass[:i]
        if cherryClass not in parsedModule.abstractClassList:
            parsedModule.cherryClassInstantiationCode += '    global %s\n    %s = %s()\n' % (cherryClassInstance, cherryClassInstance, cherryClass)

        # Inherit mask and view names from parent, except for hidden ones
        if parentList:
            for parent in parentList:
                if parent not in parsedModule.hiddenClassList:
                    parentInstance=lowerFirst(parent)
                    parentMaskAndViewMap=parsedModule.maskAndViewMap.get(parentInstance, {})
                    parentHiddenMaskAndViewMap=parsedModule.hiddenMaskAndViewMap.get(parentInstance, {})
                    if not parsedModule.maskAndViewMap.has_key(cherryClassInstance):
                        parsedModule.maskAndViewMap[cherryClassInstance]={}
                    for functionName in parentMaskAndViewMap.keys():
                        if not parentHiddenMaskAndViewMap.has_key(functionName):
                            parsedModule.maskAndViewMap[cherryClassInstance][functionName]=1

# Include aspect code at the beginning or end of a method
def writeAspect(f, cherryClass, parsedModule, method, startOrEnd):
    lines = getAspectLines(f, cherryClass, parsedModule, method, startOrEnd)
    # If startOrEnd is 'end', we have to reverse the lines to obtain the following result in the following case:
    #
    # CherryClass A:
    # aspect:
    #   (1) start:
    #       startA
    #   (1) end:
    #       endA
    # CherryClass B:
    # aspect:
    #   (1) start:
    #       startB
    #   (1) end:
    #       endB
    # CherryClass Root(A,B):
    # mask:
    #   def index(self):
    #       hello
    #
    # root.index should return "startA startB hello endB endA"
    if startOrEnd == 'end': lines.reverse() 
    f.write(''.join(lines))

def getAspectLines(f, cherryClass, parsedModule, method, startOrEnd):
    lines = []
    parentList = parsedModule.parentListMap.get(cherryClass, [])
    for parent in parentList:
        if parsedModule.aspectMap.has_key(parent):
            for key, body in parsedModule.aspectMap[parent][startOrEnd]:
                if key=='*' or eval(key):
                    extraLine = ""
                    for line2 in body.split('\n'):
                        extraLine += '        %s\n'%line2
                    lines.append(extraLine)
        # Recursive call to see if parent has aspect
        lines = getAspectLines(f, parent, parsedModule, method, startOrEnd) + lines
    return lines

def findClosingQuote(str, quote, startIndex, beforeNewline=1):
    while 1:
        i=str.find(quote, startIndex)
        if i==-1: raiseError("No closing '%s' for string '%s ...'"%(quote, str[startIndex:startIndex+20]), 0, 1, 1)
        elif str[i-1] == '\\':
            startIndex = i+1
            continue
        if beforeNewline:
            j=str.find('\n', startIndex)
            if j!=-1 and j<i:
                raiseError("No closing '%s' for string '%s ...' before the end of the line"%(quote, str[startIndex:j]), 0, 1, 1)
        return i

def findEndOfTag(str, startIndex, beforeNewline=1):
    i = findClosingQuote(str, '"', str.find('"', startIndex)+1, beforeNewline)
    if str[i+1]=='>': end = i+1
    elif str[i+1:i+3]=='/>': end = i+2
    elif str[i+1:i+4]==' />': end = i+3
    else:
        raiseError("No closing '%s' for string '%s ...'"%('">', str[startIndex:startIndex+20]), 0, 1, 1)
    if beforeNewline:
        j=str.find('\n', startIndex)
        if j!=-1 and j<i:
            raiseError("No closing '%s' for string '%s ...' before the end of the line"%('">', str[startIndex:j]), 0, 1, 1)
    return (i, end)

def findEndOfPyCode(str, startIndex):
    i = startIndex
    while 1:
        i = findClosingQuote(str, '>', i+1, 0)
        if i == -1:
            raiseError("No closing '%s' for string '%s ...'"%('">', str[startIndex:startIndex+20]), 0, 1, 1)
        elif str[i-1:i+1] == '">':
            return (i-1, i)
        elif str[i-2:i+1] == '"/>':
            return (i-2, i)
        elif str[i-3:i+1] == '" />':
            return (i-3, i)

def findClosingTag(mask, openingTag, closingTag, openTagCount, startIndex, text):
    if openTagCount<0: raiseError("Too many closing tags '%s' for '%s ... %s ...'"%(closingTag, openingTag, text), 0, 1, 1)
    i=mask.find(openingTag, startIndex)
    j=mask.find(closingTag, startIndex)
    #print "text:", text, "openCount:", openTagCount, "i:", i, "j:",j
    #if i!=-1: print "i20:", mask[i:i+20]
    #if j!=-1: print "j20:", mask[j:j+20]
    if j==-1: raiseError("No matching '%s' tag for '%s ... %s ...'"%(closingTag, openingTag, text), 0, 1, 1)
    if i==-1 or j<i: # closingTag is first
        if openTagCount==0: return j # found it !
        return findClosingTag(mask, openingTag, closingTag, openTagCount-1, j+1, text)
    else: # openingTag is first
        return findClosingTag(mask, openingTag, closingTag, openTagCount+1, i+1, text)

def findClosingDiv(mask, startIndex, text):
    return findClosingTag(mask, '<div', '</div>', 0, startIndex, text)

def findClosingPyFor(mask, startIndex, text):
    return findClosingTag(mask, '<py-for', '</py-for>', 0, startIndex, text)

def findClosingPyIf(mask, startIndex, text):
    return findClosingTag(mask, '<py-if', '</py-if>', 0, startIndex, text)

def findClosingPyElse(mask, startIndex, text):
    return findClosingTag(mask, '<py-else', '</py-else>', 0, startIndex, text)

def writeInTripleQuotes(f, str, tab):
    if str:
        str=str.replace('\\', '\\\\').replace('"""', '\\"""')
        if str[0]=='"': str='\\'+str
        if str[-1]=='"': str=str[:-1]+'\\"'
        f.write(tab+"_page.append("+quote3+str+quote3+")\n")

def expandPyInclude(mask, includeDirList, loop=0):
    if loop>100:
        raiseError("Infinite loop in 'py-include'", 0, 1, 1)
    i=mask.find("py-include")
    if i==-1: return mask
    if mask[i+10:i+12]!='="':
        raiseError("Tag 'py-include' should be followed by '=\"'", 0, 1, 1)
    j,end=findEndOfTag(mask, i)

    # Read template file
    templateFilename=mask[i+12:j]
    templateData=getModuleLines(includeDirList, templateFilename, '')

    # Replace py-include tag with template file
    if i>0 and mask[i-1]=='<':
        # CGTL tag (<py-include)
        i=i-1
        j=end
    else:
        if i>=5 and mask[i-5:i]=='<div ':
            # CHTL tag (<div py-include)
            j=findClosingDiv(mask, i, templateFilename)
            i=i-5
            j=j+5
        else:
            raiseError("'py-include' tag can be used either as '<py-include=\"...\">' or '<div py-include=\"...\">...</div>'", 0, 1, 1)

    newMask=mask[:i]
    # Add extra information to correctly report filename in case of an error
    newMask += '<PY_CURRENT_SOURCE_FILENAME="%s">\n' % templateFilename
    for data in templateData:
        newMask+='%s\n'%data
    newMask += '<PY_CURRENT_SOURCE_FILENAME="%s">\n' % parserPos.fileName
    mask=newMask[:-1]+mask[j:]
    mask=expandPyInclude(mask, includeDirList, loop+1)
    return mask

def writeMask(f, mask, tab):
    # Remove py-debug if not in debug mode
    if not _debug:
        i=mask.find('<div py-debug')
        if i!=-1:
            j=findClosingDiv(mask, i+1, "py-debug")
            writeMask(f, mask[:i]+mask[j+6:], tab)
            return
        i=mask.find('<py-debug')
        if i!=-1:
            j,end=findEndOfTag(mask, i)
            writeMask(f, mask[:i]+mask[end+1:], tab)
            return

    tagList=['py-eval', 'py-exec', 'py-code', 'py-attr', 'py-if', 'py-for', 'py-debug', 'PY_CURRENT_SOURCE_FILENAME']
    minI=len(mask)
    minTag=""
    for tag in tagList:
        i=mask.find(tag+'="')
        if i==-1: continue
        if i<minI:
            minI=i
            minTag=tag
    if not minTag or minTag == 'PY_CURRENT_SOURCE_FILENAME':
        # Check that no tags are left without '='
        # This catches common mistake: 'py-if "1==1"' instead of 'py-if="1==1"'
        if not minTag: minI=-1
        for tag in tagList:
            if mask[:minI].find(tag) !=-1:
                raiseError("Tag '%s' should be followed by '=\"'"%(tag), 0, 1, 1)
        # Check that no "py-else" are left:
        if not minTag and mask.find("py-else")!=-1:
            raiseError("Tag 'py-else' found without corresponding 'py-if'", 0, 1, 1)
        if not minTag:
            writeInTripleQuotes(f, mask, tab)
    if minTag == 'PY_CURRENT_SOURCE_FILENAME':
        j,maxI=findEndOfTag(mask, minI)
        parserPos.fileName = mask[minI+28:j]
        writeInTripleQuotes(f, mask[:minI-1], tab)
        writeMask(f, mask[maxI+2:], tab)
    elif minTag=='py-eval':
        j,maxI=findEndOfTag(mask, minI)
        evalStr=mask[minI+9:j]

        if minI>0 and mask[minI-1]=='<':

            # CGTL tag (<py-eval)
            writeInTripleQuotes(f, mask[:minI-1], tab)
            f.write(tab+'_page.append(str(%s))\n'%evalStr)
            writeMask(f, mask[maxI+1:], tab)

        else:

            # CHTL tag (<div py-eval)
            j2=mask.find('<', j)
            # Check if we have a special <div, just for the py-eval
            if minI>=5 and mask[minI-5:minI]=='<div ':
                # Special case for <div py-eval="i+2">Dummy</div>: remove <div and </div in that case
                j3=findClosingDiv(mask, minI, evalStr)
                writeInTripleQuotes(f, mask[:minI-5], tab)
                f.write(tab+'_page.append(str(%s))\n'%evalStr)
                writeMask(f, mask[j3+6:], tab)
            else:
                writeInTripleQuotes(f, mask[:minI-1]+'>', tab)
                f.write(tab+'_page.append(str(%s))\n'%evalStr)
                writeMask(f, mask[j2:], tab)

    elif minTag=='py-attr':
        j=findClosingQuote(mask, '"', minI+9)

        j2a=mask.find('="', j)
        if j2a==-1: j2a=len(mask)
        j2b=mask.find("='", j)
        if j2b==-1: j2b=len(mask)
        if j2a<j2b:
            j2=j2a
            j3=mask.find('"', j2+2)
        else:
            j2=j2b
            j3=mask.find("'", j2+2)
        evalStr=mask[minI+9:j]
        writeInTripleQuotes(f, mask[:minI-1]+mask[j+1:j2+2], tab)
        f.write(tab+'_page.append(str(%s))\n'%evalStr)
        writeMask(f, mask[j3:], tab)

    elif minTag=='py-exec':
        j,maxI=findEndOfTag(mask, minI)

        execStr=mask[minI+9:j]

        if minI>0 and mask[minI-1]=='<':

            # CGTL tag(<py-exec)
            writeInTripleQuotes(f, mask[:minI-1], tab)
            f.write(tab+execStr+'\n')
            writeMask(f, mask[maxI+1:], tab)

        else:

            # CHTL tag(<div py-exec)

            # Check that we have a </div> after the command
            if mask[j+2:j+2+6]!='</div>':
                raiseError("'<div py-exec=%s' is not closed with '</div>'"%execStr, 0, 1, 1)

            j0=mask.rfind('<div', 0, minI)
            j2=mask.find('</div>', j0)
            writeInTripleQuotes(f, mask[:j0], tab)
            f.write(tab+execStr+'\n')
            writeMask(f, mask[j2+6:], tab)

    elif minTag=='py-code':
        # Has to be used like:
        # <div py-code="
        #    i=1
        #    _page.append("%s 2"%i)
        # ">
        if mask[minI+9]!='\n':
            raiseError("'py-code=\"' must be followed by a newline", 0, 1, 1)
        j,maxI=findEndOfPyCode(mask, minI)

        execStr=mask[minI+10:j]
        # Try to indent execStr correctly
        lines=[]
        minIndent=1000
        for line in execStr.split('\n'):
            if line.split():
                indentCount = 0
                while indentCount < len(line) and line[indentCount:indentCount+4] == '    ': indentCount += 4
                if indentCount < minIndent: minIndent=indentCount
                lines.append(line)
        if minIndent==1000: minIndent=0

        if minI>0 and mask[minI-1]=='<':

            # CGTL tag(<py-code)
            writeInTripleQuotes(f, mask[:minI-1], tab)
            for line in lines:
                # Remove "minIndent" tabs and add "tab" tabs from each line
                f.write(tab+line[minIndent:]+'\n')
            writeMask(f, mask[maxI+1:], tab)

        else:

            # CHTL tag(<div py-code)

            # Check that we have a </div> after the command
            if mask[j+2:j+2+6]!='</div>':
                raiseError("'<div py-code=%s' is not closed with '</div>'"%execStr, 0, 1, 1)

            j0=mask.rfind('<div', 0, minI)
            j2=mask.find('</div>', j0)
            writeInTripleQuotes(f, mask[:j0], tab)
            for line in lines:
                # Remove "minIndent" tabs and add "tab" tabs from each line
                f.write(tab+line[minIndent:]+'\n')
            writeMask(f, mask[j2+6:], tab)

    elif minTag=='py-for':
        j=findClosingQuote(mask, '">', minI)

        forStr=mask[minI+8:j]

        if minI>0 and mask[minI-1]=='<':

            # CGTL (<py-for ... </py-for>)
            j2=findClosingPyFor(mask, j, forStr)
            text=mask[j+2:j2]
            writeInTripleQuotes(f, mask[:minI-1], tab)
            # Save old _index and _end because we are going to mess with them
            f.write(tab+'_index%s=locals().get("_index", -1)\n' % len(tab))
            f.write(tab+'_end%s=locals().get("_end", -1)\n' % len(tab))
            f.write(tab+'_index=-1\n')
            try:
                f.write(tab+'try: _end=len(%s)-1\n' % forStr.split(' in ')[1]) # Set _end
                f.write(tab+'except TypeError: _end=-1\n') # Because Generators don't have a length
            except IndexError:
                raiseError("py-for string '%s' is not correct"%forStr, 0, 1, 1)
            f.write(tab+'for '+forStr+':\n')
            f.write(tab+'    _index+=1\n')
            writeMask(f, text, tab+'    ')
            # Restore old _index and _end
            f.write(tab+'_index=_index%s\n' % len(tab))
            f.write(tab+'_end=_end%s\n' % len(tab))
            writeMask(f, mask[j2+9:], tab)

        else:

            # CHTL (<div py-for ... </div>)
            j0=mask.rfind('<div', 0, minI)
            # Find matching </div> (warning: could be nested)
            j2=findClosingDiv(mask, j0+1, forStr)
            text=mask[j+2:j2]
            writeInTripleQuotes(f, mask[:j0], tab)
            # Save old _index and _end because we are going to mess with them
            f.write(tab+'_index%s=locals().get("_index", -1)\n' % len(tab))
            f.write(tab+'_end%s=locals().get("_end", -1)\n' % len(tab))
            f.write(tab+'_index=-1\n')
            try:
                f.write(tab+'try: _end=len(%s)-1\n' % forStr.split(' in ')[1]) # Set _end
                f.write(tab+'except TypeError: _end=-1\n') # Because Generators don't have a length
            except IndexError:
                raiseError("py-for string '%s' is not correct"%forStr, 0, 1, 1)
            f.write(tab+'for '+forStr+':\n')
            f.write(tab+'    _index+=1\n')
            writeMask(f, text, tab+'    ')
            # Restore old _index and _end
            f.write(tab+'_index=_index%s\n' % len(tab))
            f.write(tab+'_end=_end%s\n' % len(tab))
            writeMask(f, mask[j2+6:], tab)

    elif minTag=='py-if':
        j=findClosingQuote(mask, '">', minI)

        ifStr=mask[minI+7:j]

        if minI>0 and mask[minI-1]=='<':

            # CGTL (<py-if ... </py-if>   <py-else>...</py-else>)
            j2=findClosingPyIf(mask, j, ifStr)
            ifText=mask[j+2:j2]
            # Check if there is a <py-else>
            k=j2+8 # k will be the index of the next significant character after </py-if>
            while k<len(mask):
                if '    \r\n '.find(mask[k])==-1: break
                k+=1
            if k!=len(mask) and mask[k:k+9]=='<py-else>':
                j3=findClosingPyElse(mask, k+9, ifStr+" else ")
                elseText=mask[k+9:j3]
                j4=j3+10
            else:
                elseText=""
                j4=j2+8
            #print "ifStr:",ifStr
            writeInTripleQuotes(f, mask[:minI-1], tab)
            f.write(tab+'if %s:\n'%ifStr)
            writeMask(f, ifText, tab+'    ')
            if elseText:
                f.write(tab+'else:\n')
                writeMask(f, elseText, tab+'    ')
            writeMask(f, mask[j4:], tab)

        else:

            # CHTL (<div py-if ... </div>   <div py-else>...</div>)
            j0=mask.rfind('<div', 0, minI)
            # Find matching </div> (warning: could be nested)
            j2=findClosingDiv(mask, j0+1, ifStr)
            ifText=mask[j+2:j2]
            # Check if there is a py-else>
            k=j2+6 # k will be the index of the next significant character after </div>
            while k<len(mask):
                if '    \r\n '.find(mask[k])==-1: break
                k+=1
            if k!=len(mask) and mask[k:k+13]=='<div py-else>':
                j3=findClosingDiv(mask, k+13, ifStr+" else ")
                elseText=mask[k+13:j3]
            else:
                elseText=""
                j3=j2
            #print "ifStr:",ifStr
            writeInTripleQuotes(f, mask[:j0], tab)
            f.write(tab+'if %s:\n'%ifStr)
            writeMask(f, ifText, tab+'    ')
            if elseText:
                f.write(tab+'else:\n')
                writeMask(f, elseText, tab+'    ')
            writeMask(f, mask[j3+6:], tab)

    elif minTag=='py-debug':
        j,maxI=findEndOfTag(mask, minI)
        debugStr=mask[minI+10:j]

        if minI>0 and mask[minI-1]=='<':

            # CGTL tag (<py-debug)
            writeInTripleQuotes(f, mask[:minI-1], tab)
            f.write(tab+'debug(%s)\n'%debugStr)
            writeMask(f, mask[maxI+1:], tab)

        else:

            # CHTL tag (<div py-debug)
            j0=mask.rfind('<div', 0, minI)
            # Find matching </div> (warning: could be nested)
            j2=findClosingDiv(mask, j0+1, debugStr)
            writeInTripleQuotes(f, mask[:j0], tab)
            f.write(tab+'debug(%s)\n'%debugStr)
            writeMask(f, mask[j2+6:], tab)

    elif minTag: raise "Internal error: minTag= '%s'" % minTag


def writeFunction(f, cherryClass, parsedModule, currentMap, section):
    if currentMap.has_key(section) and currentMap[section]:
        # print "    Writing",section
        # Break up lines by function
        functionBodyList=[]
        functionBody=""
        # print "CurrentMap[%s]: %s" % (section, repr(currentMap[section]))
        for line in currentMap[section].split('\n'):
            # print "line:", repr(line)
            if line[:4]=='def ':
                # New function
                if functionBody: functionBodyList.append(functionBody)
                functionBody='    '+line+'\n'
                # Check that programmer didn't forget "self" as first argument
                i = line.find('(')
                errorMsg = "Expected function definition 'def func(self ...' instead of '%s'"%line
                if i == -1: raiseError(errorMsg, 0, 1, 0)
                j = line.find(',', i)
                k = line.find(')', i)
                if j == -1: j = k
                elif k == -1: pass
                else: j = min([j,k])
                if line[i+1:j].strip() != 'self': raiseError(errorMsg, 0, 1, 0)
            else:
                # Add 4 whitespaces for functions and views, remove 4 whitespaces for masks
                if section=='mask':
                    functionBody+=line[4:]+'\n'
                else:
                    functionBody+='    '+line+'\n'
        functionBodyList.append(functionBody)

        # Write functions
        for functionBody in functionBodyList:
            i=functionBody.find('\n')
            functionDef=functionBody[:i+1]

            # Get function name
            j=functionDef.find('(')
            # Make method class that will be evaluated to match aspect
            method=emptyClass()
            method.className=cherryClass
            method.name=functionDef[8:j] # 8 because we have a '    ' at the beginning !
            parserPos.methodName=method.name
            method.type=section
            if cherryClass in parsedModule.hiddenClassList: method.isHidden=1
            else: method.isHidden=0
            if cherryClass in parsedModule.xmlrpcClassList: method.isXmlrpc=1
            else: method.isXmlrpc=0
            # print "        Writing %s %s"%(method.type,method.name)

            # Save view and mask names
            if method.type in ['view', 'mask']:
                cherryClassInstance=lowerFirst(cherryClass)
                if not parsedModule.maskAndViewMap.has_key(cherryClassInstance): parsedModule.maskAndViewMap[cherryClassInstance]={}
                parsedModule.maskAndViewMap[cherryClassInstance][method.name]=1

            if functionDef.rstrip()[-7:]=="hidden:":
                if method.type not in ['view', 'mask']:
                    raiseError('Only views and masks can be hidden', 0, 1, 0)
                if not parsedModule.hiddenMaskAndViewMap.has_key(cherryClassInstance): parsedModule.hiddenMaskAndViewMap[cherryClassInstance]={}
                parsedModule.hiddenMaskAndViewMap[cherryClassInstance][method.name]=1
                functionDef=functionDef.rstrip()[:-7]+":\n"
                method.isHidden=1

            if functionDef.rstrip()[-7:]=="xmlrpc:":
                if not parsedModule.xmlrpcMaskAndViewMap.has_key(cherryClassInstance): parsedModule.xmlrpcMaskAndViewMap[cherryClassInstance]={}
                parsedModule.xmlrpcMaskAndViewMap[cherryClassInstance][method.name]=1
                functionDef=functionDef.rstrip()[:-7]+":\n"
                method.isXmlrpc=1

            # Write function header
            f.write(functionDef)

            # Write function body, with aspect at the beginning or at the end
            # If it's a mask, declare _page before "aspect start" and return _page after "aspect end"
            if section=='mask':
                f.write('        _page=[]\n')
            writeAspect(f, cherryClass, parsedModule, method, 'start')
            if section=='mask':
                #print "writing mask:", method.name
                parserPos.maskName = method.name
                mask=functionBody[i+1:]
                mask=expandPyInclude(mask, includeDirList)
                writeMask(f, mask, '        ')
            else:
                # print "functionBody:", functionBody[i+1:]
                f.write(functionBody[i+1:])
            writeAspect(f, cherryClass, parsedModule, method, 'end')
            if section=='mask':
                # print "Writing join"
                f.write('        return "".join(_page)\n')

def getModuleLines(includeDirList, fileName, extension):
    fileNameBase,fileNameExtension = os.path.splitext(fileName)
    if fileNameExtension!=extension:
        fileName+=extension
    if not os.path.isabs(fileName):
        # Relative path search
        for dirName in includeDirList:
            fileRelName=os.path.join(dirName,fileName)
            if os.path.exists(fileRelName):
                fileName=fileRelName
                break
        else:
            raise 'CherryError: Cannot find file %s'%`fileName`
    data=open(fileName,'r').read()
    lines=data.splitlines()
    newLines=[]
    for line in lines:
        # Find the first character in the line that's not a whitespace and not a tab
        i = 0
        foundOne = 0
        while i < len(line):
            if line[i] not in (' ', '\t'):
                foundOne = 1
                break
            else: i += 1
        if foundOne:
            startLine = line[:i]
            endLine = line[i:]
            # Replace all blocks of ' '*whiteSpace with ' '*4
            if whiteSpace != 4: startLine = startLine.replace(' '*whiteSpace, '    ')
            # Replace all tabs with ' '*4
            startLine = startLine.replace('\t', '    ')
            line = startLine + endLine

        newLines.append(line)
    return newLines

def printUsageAndExit():
    print "CherryPy version %s. See http://www.cherrypy.org for more information"%version
    print "Usage: CherryPy [-D] [--stderr2stdout] [-W whiteSpace] [-I includeDirectory] [-O outputFile] [-S|--shebang shebang] [-E|--encoding encoding] file"
    sys.exit(-1)

# Parse arguments
if os.environ.has_key('CHERRYPY_HOME'):
    home=os.environ['CHERRYPY_HOME']
    if home[0] in "'\"": home=home[1:-1]
    includeDirList=[os.path.join(home,'lib'), os.path.join(home,'src')]
else:
    includeDirList=[os.path.join('..','lib'), os.path.join('..','src')]
# Optimizing path
includeDirList=filter(os.path.exists,includeDirList)
outputFile=""
shebang=""
encoding=""
_debug=0
hotReload=0
whiteSpace=4
staticDirList=[]
try:
    optList, args=getopt.getopt(sys.argv[1:], 'W:I:O:S:E:DV', ['stderr2stdout', 'shebang=', 'encoding='])
except getopt.GetoptError:
    printUsageAndExit()
for optionKey, optionValue in optList:
    if optionKey=='-W':
        try:
            whiteSpace=int(optionValue)
            if whiteSpace<1 or whiteSpace>20: raise "Error"
        except:
            print "CherryError: whiteSpace must be between 1 and 20"
            printUsageAndExit()
    elif optionKey=='-I': includeDirList.append(optionValue)
    elif optionKey=="--stderr2stdout":
        sys.stderr=sys.stdout
    elif optionKey=="-D":
        _debug=1
    elif optionKey=="-O":
        if outputFile: printUsageAndExit()
        else: outputFile=optionValue
    elif optionKey=="-V":
        print version
        sys.exit(1)
    elif optionKey in ("-S", "--shebang"):
        shebang = optionValue + '\n'
    elif optionKey in ("-E", "--encoding"):
        encoding = "# -*- coding: %s -*-" % optionValue + '\n'
    else: printUsageAndExit()
if not args: printUsageAndExit()
mainFile=args[0]
if not outputFile:
    i=mainFile.find('.')
    if i==-1: i=len(mainFile)
    outputFile=mainFile[:i]+'Server.py'
i=outputFile.find('.py')
if i==-1: outputFileBase=outputFile
else: outputFileBase=outputFile[:i]

includeDirList.append('.') # Current directory is always first for searching files
includeDirList.reverse() # Look first in directories specified on the command line

# read all files to get list of files and order to parse
dependencyMap={}
alreadyLoaded=[]
toBeLoaded=[]
for arg in args:
    i=arg.find('.cpy')
    if i!=-1: toBeLoaded.append(arg[:i])
    else: toBeLoaded.append(arg)
while 1:
    currentModule=toBeLoaded.pop()
    alreadyLoaded.append(currentModule)
    lines=getModuleLines(includeDirList, currentModule, '.cpy')
    dependencyMap[currentModule]=[]
    for i in xrange(len(lines)):
        if lines[i][:4]=='use ':
            line=string.join(lines[i][4:].split(), '')
            moduleList=line.split(',')
            newModuleList=[]
            for module in moduleList:
                i=module.find('.cpy')
                if i!=-1: newModuleList.append(module[:i])
                else: newModuleList.append(module)
            dependencyMap[currentModule]+=newModuleList
            for module in moduleList:
                if module not in toBeLoaded and module not in alreadyLoaded:
                    toBeLoaded.append(module)
        else:
            break
    if not toBeLoaded: break


# read modules in right order (according to dependencyMap)
parsedModule=emptyClass()
parsedModule.cherryClassList=[]
parsedModule.parentListMap={}
parsedModule.cherryClassInstantiationCode = ""
parsedModule.abstractClassList=[]
parsedModule.hiddenClassList=[]
parsedModule.xmlrpcClassList=[]
parsedModule.hiddenMaskAndViewMap={}
parsedModule.xmlrpcMaskAndViewMap={}
parsedModule.aspectMap={}
parsedModule.importList=[]
parsedModule.initRequestBeforeParse="def initRequestBeforeParse():\n    pass\n"
parsedModule.initRequest="def initRequest():\n    pass\n"
parsedModule.initNonStaticRequest="def initNonStaticRequest():\n    pass\n"
parsedModule.initResponse="def initResponse():\n    pass\n"
parsedModule.initNonStaticResponse="def initNonStaticResponse():\n    pass\n"
parsedModule.initServer="def initServer():\n    pass\n"
parsedModule.initProgram=""
parsedModule.initThread="def initThread(threadIndex):\n    pass\n"
parsedModule.initProcess="def initProcess(processIndex):\n    pass\n"
parsedModule.initAfterBind="def initAfterBind():\n    pass\n"
parsedModule.hotReloadInitServer="def hotReloadInitServer():\n    pass\n"
parsedModule.onError="def onError():\n"
parsedModule.logMessage="def logMessage(message, level=0):\n"
parsedModule.saveSessionData="def saveSessionData(sessionId, sessionData, expirationTime):\n    pass\n"
parsedModule.loadSessionData="def loadSessionData(sessionId):\n    pass\n"
parsedModule.cleanUpOldSessions="def cleanUpOldSessions():\n    pass\n"
parsedModule.maskAndViewMap={}
parsedModule.includeDirList=includeDirList

# Use class to store current file that's being parsed
parserPos=emptyClass()
parserPos.fileName=""
parserPos.lineIndex=0
parserPos.cherryClassName=""
parserPos.maskName=""

while 1:
    foundModule=0
    for module, dependencyList in dependencyMap.items():
        if not dependencyList: # We found a module that doesn't depend on another one
            parseModule(parsedModule, module)
            # Remove module from all dependencyLists
            del dependencyMap[module]
            for dependencyList in dependencyMap.values():
                if module in dependencyList:
                    dependencyList.remove(module)
            foundModule=1
            break
    if not dependencyMap: break
    if not foundModule: raise "CherryError: Infinite loop in modules dependency"

if parsedModule.onError=="def onError():\n":
    # Default onError
    parsedModule.onError="""
def onError():
    import traceback, StringIO
    bodyFile=StringIO.StringIO()
    traceback.print_exc(file=bodyFile)
    response.body=bodyFile.getvalue()
    bodyFile.close()
    response.headerMap['content-type']='text/plain'
    if request.isXmlRpc:
        # Special case for XML-RPC:
        response.body=xmlrpclib.dumps(xmlrpclib.Fault(1, response.body))
        response.headerMap['content-type']='text/xml'
"""

if parsedModule.logMessage=="def logMessage(message, level=0):\n":
    # Default logMessage
    parsedModule.logMessage="""
def logMessage(message, level=0):
    if level: return
    if _logToScreen: print message
    if _logFile:
        f=open(_logFile, "a")
        f.write(message+"\\n")
        f.close()
"""

    
f=open(outputFile, 'w')
f.write("""%s%s
##################################################################
# This file was generated by CherryPy-%s
# For more information about CherryPy, see http://www.cherrypy.org
##################################################################

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

""" % (shebang, encoding, version))

for line in parsedModule.initProgram.splitlines():
    f.write(line[4:]+'\n')
f.write('\n')

f.write(string.join(parsedModule.importList, '\n'))

f.write("\n_debugFile='%s'\n"%(outputFileBase+'.dbg'))
f.write("configFileName='%s'\n"%(outputFileBase+'.cfg'))
f.write("_debug=%s\n"%_debug)
f.write('_outputFile="%s"\n'%outputFile)
f.write('_outputFile="%s"\n'%outputFile)
f.write('_cacheMap={}\n')

# Write all cherryClass
writeCherryClass(f, parsedModule)

f.write("""
import string, time, urllib, sys, getopt, cgi, socket, os, ConfigParser, cStringIO, binascii, md5

_lastCacheFlushTime=time.time()
_lastSessionCleanUpTime=time.time()

def debug(debugStr):
    if _debug:
        f=open(_debugFile, 'a')
        f.write(debugStr+'\\n')
        f.close

def printUsageAndExit():
    print "Usage: server [-C configFile]"
    sys.exit(-1)

def mainInit(argv):
    global configFile, configFileName
    if not globals().has_key('hotReload'):
        if not (len(argv)==1 or (len(argv)==3 and argv[1]=="-C")): printUsageAndExit()
        if len(argv)==3: configFileName=argv[2]

    configFile=ConfigParser.ConfigParser()
    configFile.read(configFileName)
""")
# Parse config file
sourceCode=getModuleLines(includeDirList, 'parseConfigFile', '.py')
f.write("    if not globals().has_key('hotReload'):\n")
for sourceLine in sourceCode:
    if not (sourceLine and sourceLine[0] == '#'):
        f.write('        '+sourceLine+'\n')

f.write(parsedModule.cherryClassInstantiationCode)

f.write("""
    if not globals().has_key('hotReload'):
        # Call initServer function
        # logMessage("Calling initServer() ...")
        initServer()
    else:
        # Call hotReloadInitServer function
        # logMessage("Calling hotReloadInitServer() ...")
        hotReloadInitServer()
        logMessage("Hot reload finished")

    # Create request and response instances (the same will be used all the time)
    global request, response
    if not _threading and _threadPool==1:
        # If we don't use threading, we don't care about concurrency issues among different requests
        class _emptyClass: pass
        request=_emptyClass()
        response=_emptyClass()
    else:
        # If we use threading, we have to store request informations in thread-aware classes
        global _myThread
        import thread as _myThread # Ugly hack because CherryForum uses the keyword "thread" ... TBC
        class _threadAwareClass:
            def __init__(self, name):
                self.__dict__['threadMap']={} # Used to store variables. Keys are thread identifier
                self.__dict__['name']=name
            def __setattr__(self, name, value):
                if self.__dict__['name'] == 'request' and name == 'sessionMap' and not _sessionStorageType:
                    raise "You are trying to use sessions but sessions are not enabled in the config file. Check out the HowTo about sessions on the cherrypy.org website to learn how to use sessions."
                _myId=_myThread.get_ident()
                if not self.__dict__['threadMap'].has_key(_myId): self.__dict__['threadMap'][_myId]={}
                self.threadMap[_myId][name]=value
            def __getattr__(self, name):
                if self.__dict__['name'] == 'request' and name == 'sessionMap' and not _sessionStorageType:
                    raise "You are trying to use sessions but sessions are not enabled in the config file. Check out the HowTo about sessions on the cherrypy.org website to learn how to use sessions."
                _myId=_myThread.get_ident()
                return self.__dict__['threadMap'][_myId][name]
        request=_threadAwareClass('request')
        response=_threadAwareClass('response')

    # Create sessionMap if needed
    if _sessionStorageType=="ram":
        global _sessionMap
        _sessionMap={} # Map of "cookie" -> ("session object", "expiration time")

    global _weekdayname, _monthname
    _weekdayname=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    _monthname=[None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    sys.stdout.flush()

""")


# Write special functions
for specialFunction in specialFunctionList:
    if specialFunction != 'initProgram()':
        i = specialFunction.find('(')
        if _debug: f.write('global %s\n' % specialFunction[:i])
        f.write(getattr(parsedModule, specialFunction[:i]))
if _debug: f.write('global maskAndViewMap\n')
if _debug: f.write('global xmlrpcMaskAndViewMap\n')


f.write("""
def ramOrFileOrCookieOrCustomSaveSessionData(sessionId, sessionData, expirationTime):
    # Save session to file if needed
    t = time.localtime(expirationTime)
    if _sessionStorageType=='file':
        fname=os.path.join(_sessionStorageFileDir,sessionId)
        if _threadPool>1 or _threading:
            _sessionFileLock.acquire()
        f=open(fname,"wb")
        cPickle.dump((sessionData, expirationTime), f)
        f.close()
        if _threadPool>1 or _threading:
            _sessionFileLock.release()

    elif _sessionStorageType=="ram":
        # Update expiration time
        _sessionMap[sessionId]=(sessionData, expirationTime)

    elif _sessionStorageType == "cookie":
        global _SITE_KEY_
        if not globals().has_key('_SITE_KEY_'):
            # Get site key from config file or compute it
            try: _SITE_KEY_ = configFile.get('server','siteKey')
            except:
                _SITE_KEY_ = ''
                for i in range(30):
                    _SITE_KEY_ += whrandom.choice(string.letters)
        # Update expiration time
        _sessionData = (sessionData, expirationTime)
        _dumpStr = cPickle.dumps(_sessionData)
        try: _dumpStr = zlib.compress(_dumpStr)
        except: pass # zlib is not available in all python distros
        _dumpStr = binascii.hexlify(_dumpStr) # Need to hexlify it because it will be stored in a cookie
        response.simpleCookie['CSession']=_dumpStr
        response.simpleCookie['CSession-sig']=md5.md5(_dumpStr+_SITE_KEY_).hexdigest()
        response.simpleCookie['CSession']['path']='/'
        response.simpleCookie['CSession']['max-age']=_sessionTimeout*60
        response.simpleCookie['CSession-sig']['path']='/'
        response.simpleCookie['CSession-sig']['max-age']=_sessionTimeout*60

    else:
        # custom
        saveSessionData(sessionId, sessionData, expirationTime)

def ramOrFileOrCookieOrCustomLoadSessionData(sessionId):
    # Return the session data for a given sessionId. the _expirationTime will be checked by the caller of this function
    if _sessionStorageType=="ram":
        if _sessionMap.has_key(sessionId): return _sessionMap[sessionId]
        else: return None

    elif _sessionStorageType=="file":
        _fname=os.path.join(_sessionStorageFileDir,sessionId)
        if os.path.exists(_fname):
            if _threadPool>1 or _threading:
                _sessionFileLock.acquire()
            _f=open(_fname,"rb")
            _sessionData = cPickle.load(_f)
            _f.close()
            if _threadPool>1 or _threading:
                _sessionFileLock.release()
            return _sessionData
        else: return None

    elif _sessionStorageType == "cookie":
        global _SITE_KEY_
        if not globals().has_key('_SITE_KEY_'):
            try: _SITE_KEY_ = configFile.get('server','siteKey')
            except:
                return None
        if request.simpleCookie.has_key('CSession') and request.simpleCookie.has_key('CSession-sig'):
            _data = request.simpleCookie['CSession'].value
            _sig  = request.simpleCookie['CSession-sig'].value
            if md5.md5(_data + _SITE_KEY_).hexdigest() == _sig:
                try:
                    _dumpStr = binascii.unhexlify(_data)
                    try: _dumpStr = zlib.decompress(_dumpStr)
                    except: pass # zlib is not available in all python distros
                    _dumpStr = cPickle.loads(_dumpStr)
                    return _dumpStr
                except: pass
        return None

    else:
        # custom
        return loadSessionData(sessionId)

def ramOrFileOrCookieOrCustomCleanUpOldSessions():
    # Clean up old session data
    _now = time.time()
    if _sessionStorageType=="ram":
        _sessionIdToDeleteList = []
        for _sessionId, (_dummy, _expirationTime) in _sessionMap.items():
            if _expirationTime < _now: _sessionIdToDeleteList.append(_sessionId)
        for _sessionId in _sessionIdToDeleteList: del _sessionMap[_sessionId]

    elif _sessionStorageType=="file":
        # This process is *very* expensive because we go through all files, parse them and them delete them if the session is expired
        # One optimization would be to just store a list of (sessionId, expirationTime) in *one* file
        _sessionFileList = os.listdir(_sessionStorageFileDir)
        for _sessionId in _sessionFileList:
            try:
                _dummy, _expirationTime = ramOrFileOrCookieOrCustomLoadSessionData(_sessionId)
                if _expirationTime < _now:
                    os.remove(os.path.join(_sessionStorageFileDir, _sessionId))
            except: pass

    elif _sessionStorageType == "cookie":
        # Nothing to do in this case: the session data is stored on the client
        pass

    else:
        # custom
        cleanUpOldSessions()

""")

# Remove non-public mask and views from maskAndViewMap
# First, remove abstract classes
for abstractClass in parsedModule.abstractClassList:
    try: del parsedModule.maskAndViewMap[lowerFirst(abstractClass)]
    except: pass
# Remove hidden classes
for hiddenClass in parsedModule.hiddenClassList:
    try: del parsedModule.maskAndViewMap[lowerFirst(hiddenClass)]
    except: pass
# Remove hidden masks and views
for hiddenClass,hiddenMethodMap in parsedModule.hiddenMaskAndViewMap.items():
    for hiddenMethod in hiddenMethodMap.keys():
        try: del parsedModule.maskAndViewMap[hiddenClass][hiddenMethod]
        except: pass
# Copy xmlrpc classes to xmlrpcMaskAndViewMap
for xmlrpcClass in parsedModule.xmlrpcClassList:
    xmlrpcClassInstance=lowerFirst(xmlrpcClass)
    parsedModule.xmlrpcMaskAndViewMap[xmlrpcClassInstance]={}
    methodMap=parsedModule.maskAndViewMap.get(xmlrpcClassInstance, {})
    for methodName in methodMap.keys():
        parsedModule.xmlrpcMaskAndViewMap[xmlrpcClassInstance][methodName]=1

f.write("maskAndViewMap=%s\n"%`parsedModule.maskAndViewMap`)
f.write("xmlrpcMaskAndViewMap=%s\n"%`parsedModule.xmlrpcMaskAndViewMap`)

# Write http code
f.write("if not globals().has_key('hotReload'):\n")
sourceCode=getModuleLines(includeDirList, 'httpTools', '.py')
for sourceLine in sourceCode:
    if not (sourceLine and sourceLine[0] == '#'):
        f.write('    '+sourceLine+'\n')
sourceCode=getModuleLines(includeDirList, 'httpThreadPoolServer', '.py')
for sourceLine in sourceCode:
    if not (sourceLine and sourceLine[0] == '#'):
        f.write('    '+sourceLine+'\n')
sourceCode=getModuleLines(includeDirList, 'httpServer', '.py')
for sourceLine in sourceCode:
    if not (sourceLine and sourceLine[0] == '#'):
        f.write('    '+sourceLine+'\n')

f.write("""
if __name__ == '__main__':
    import sys
    run(sys.argv)
""")

f.close()
