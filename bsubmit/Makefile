bsubmit:
	g++ -o bsubmit bsubmit.cpp

install: bsubmit
	cp -f bsubmit $(LSF_BINDIR)
	chown root:root $(LSF_BINDIR)/bsubmit
	chmod u+s $(LSF_BINDIR)/bsubmit

clean:
	rm -rf bsubmit
