baseUrl="http://localhost:8000"
newBaseUrl="http://www.cherrypy.org"
forbiddenUrlList=["prestation", ".gif", ".pdf", ".ps", "mailto:", "Protected"]

import urllib

def getUrl(url):
    f=urllib.urlopen(url)
    data=f.read()
    f.close()
    return data

def getLinkList(currentUrl, data):
    currentBaseUrl='/'.join(currentUrl.split('/')[:-1])
    urlMap={}
    lowData=data.lower()
    i=-1
    while 1:
        i=lowData.find("href=", i+1)
        if i==-1: return urlMap.keys()
        if lowData[i+5]=='"' or lowData[i+5]=="'": i+=6
        else: i+=5
        j=lowData.find('"', i)
        if j==-1: j=1000000
        k=lowData.find("'", i)
        if k==-1: k=1000000
        l=lowData.find(' ', i)
        if l==-1: l=1000000
        j=min([j,k,l])
        url=data[i:j]
        j=url.find('#')
        if j!=-1: url=url[:j] # Remove '#' in url
        wrongUrl=0
        if not url: wrongUrl=1
        else:
            if url[0]=='/': url=baseUrl+url
            if url[:7]!='http://': # Relative Url
                url=currentBaseUrl+'/'+url
            if url.find(baseUrl)!=0: wrongUrl=1
            for forbiddenUrl in forbiddenUrlList:
                if url.find(forbiddenUrl)!=-1:
                    wrongUrl=1
                    break
        if not wrongUrl: urlMap[url]=None

def extractTitle(data):
    # Get title
    i=data.lower().find("<title>")
    if i==-1: return "No title"
    j=data.lower().find("</title>")
    title=data[i+7:j]
    return title

def extractText(data):
    # Remove html tags between < and >
    while 1:
        i=data.find('<')
        if i==-1: break
        j=data.find('>', i)
        if j!=-1: data=data[:i]+' '+data[j+1:]
        else: break
    return data

def getKeyWordMap(data):
    # First of all, we strip out all html tags
    strippedData=extractText(data)
    # Then we replace all non-conventional characters with spaces
    for i in range(len(strippedData)):
        c=strippedData[i]
        if (not 'a'<=c<='z') and (not 'A'<=c<='Z') and (not '0'<=c<='9'):
            strippedData=strippedData[:i]+' '+strippedData[i+1:]
    keyWordMap={}
    for keyWord in strippedData.lower().split():
        keyWordMap[keyWord]=keyWordMap.get(keyWord, 0)+1
    return keyWordMap

urlToProcess=[baseUrl]
processedUrl=[]
keyWordMap={} # keyword->list of (urls, title, score)

while urlToProcess:
    url=urlToProcess.pop()
    print "******* Reading url:", url
    processedUrl.append(url)
    data=getUrl(url)
    # Get list of links
    newUrlList=getLinkList(url, data)
    # print "linkList:", newUrlList
    for newUrl in newUrlList:
        if newUrl not in processedUrl and newUrl not in urlToProcess: urlToProcess.append(newUrl)
    # Get keyword map
    pageKeyWordMap=getKeyWordMap(data)
    title=extractTitle(data)
    #print "keyWord:",
    url=url.replace(baseUrl, newBaseUrl)
    for keyWord, score in pageKeyWordMap.items():
        #print keyWord,
        if not keyWordMap.has_key(keyWord): keyWordMap[keyWord]=[(url, title, score)]
        else: keyWordMap[keyWord].append((url, title, score))

import cPickle
f=open("keyWordMap", "w")
cPickle.dump(keyWordMap, f)
f.close()

print "keyWordMap dumped"
