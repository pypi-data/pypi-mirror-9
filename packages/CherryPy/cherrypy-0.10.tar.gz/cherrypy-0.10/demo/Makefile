all: DemoServer.py
DemoServer.py: Root.cpy Demo.cpy Prestation.cpy PrestationFrench.cpy PrestationEnglish.cpy PrestationTables.cpy
	python ../cherrypy.py Root.cpy

clean:
	rm -f DemoServer.py
