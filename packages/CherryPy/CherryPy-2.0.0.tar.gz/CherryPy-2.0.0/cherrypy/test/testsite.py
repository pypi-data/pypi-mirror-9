
import sys,os,os.path
sys.path.insert(0,os.path.normpath(os.path.join(os.getcwd(),'../../')))

from cherrypy import cpg
from cherrypy.lib.filter import basefilter, virtualhostfilter

siteMap = {
    'site1': '/site1',
    'site2': '/site2'
}

class Site1Filter(basefilter.BaseOutputFilter):
    def beforeResponse(self):
        cpg.response.body += 'Site1Filter'
class Site2Filter(basefilter.BaseOutputFilter):
    def beforeResponse(self):
        cpg.response.body += 'Site2Filter'

class Root:
    _cpFilterList = [virtualhostfilter.VirtualHostFilter(siteMap)]

class Site1:
    _cpFilterList = [Site1Filter()]
    def index(self):
        return "SITE1"
    index.exposed = True
class Site2:
    _cpFilterList = [Site2Filter()]
    def index(self):
        return "SITE2"
    index.exposed = True

cpg.root = Root()
cpg.root.site1 = Site1()
cpg.root.site2 = Site2()

class Shutdown:
    def all(self):
        cpg.server.stop()
        return ""
    all.exposed = True
cpg.root.shutdown = Shutdown()
def f(*a, **kw): return ""
cpg.root._cpLogMessage = f
cpg.server.start(configFile = 'testsite.cfg')
