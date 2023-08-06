OPTION=--html --about html/stdabout.dat --address "See <i><a href=\"about.html\">About this document...</a></i> for information on suggesting changes." --numeric --split 3 --dvips-safe 
all: tut howto lib
tut: tut/tut.tex
	python tools/mkhowto $(OPTION) --dir html/tut tut/tut.tex
	cd paper-letter && python ../tools/mkhowto --paper=letter --pdf ../tut/tut.tex
	cd paper-letter && python ../tools/mkhowto --paper=letter --dvi ../tut/tut.tex
	cd paper-letter && dvips -N0 -t letter tut.dvi -o tut.ps
	cd paper-a4 && python ../tools/mkhowto --paper=a4 --pdf ../tut/tut.tex
	cd paper-a4 && python ../tools/mkhowto --paper=a4 --dvi ../tut/tut.tex
	cd paper-a4 && dvips -N0 -t a4 tut.dvi -o tut.ps
tut-it: tut-it/tut.tex
	python tools/mkhowto $(OPTION) --dir html/tut-it tut-it/tut.tex
	cd paper-letter && python ../tools/mkhowto --paper=letter --pdf ../tut-it/tut.tex
	cd paper-letter && python ../tools/mkhowto --paper=letter --dvi ../tut-it/tut.tex
	cd paper-letter && dvips -N0 -t letter tut.dvi -o tut.ps
	cd paper-a4 && python ../tools/mkhowto --paper=a4 --pdf ../tut-it/tut.tex
	cd paper-a4 && python ../tools/mkhowto --paper=a4 --dvi ../tut-it/tut.tex
	cd paper-a4 && dvips -N0 -t a4 tut.dvi -o tut.ps
howto: howto/howto.tex
	python tools/mkhowto $(OPTION) --dir html/howto  howto/howto.tex
	cd paper-letter && python ../tools/mkhowto --paper=letter --pdf ../howto/howto.tex
	cd paper-letter && python ../tools/mkhowto --paper=letter --dvi ../howto/howto.tex
	cd paper-letter && dvips -N0 -t letter howto.dvi -o howto.ps
	cd paper-a4 && python ../tools/mkhowto --paper=a4 --pdf ../howto/howto.tex
	cd paper-a4 && python ../tools/mkhowto --paper=a4 --dvi ../howto/howto.tex
	cd paper-a4 && dvips -N0 -t a4 howto.dvi -o howto.ps
lib: lib/lib.tex
	python tools/mkhowto --html --about html/stdabout.dat --address "See <i><a href=\"about.html\">About this document...</a></i> for information on suggesting changes." --global-module-index "../modindex.html" --dvips-safe --dir html/lib lib/lib.tex
	cd paper-letter && python ../tools/mkhowto --paper=letter --pdf ../lib/lib.tex
	cd paper-letter && python ../tools/mkhowto --paper=letter --dvi ../lib/lib.tex
	cd paper-letter && dvips -N0 -t letter lib.dvi -o lib.ps
	cd paper-a4 && python ../tools/mkhowto --paper=a4 --pdf ../lib/lib.tex
	cd paper-a4 && python ../tools/mkhowto --paper=a4 --dvi ../lib/lib.tex
	cd paper-a4 && dvips -N0 -t a4 lib.dvi -o lib.ps
