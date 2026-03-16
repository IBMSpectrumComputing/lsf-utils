bsubkill:
	g++ -o bsubkill bsubkill.cpp

install: bsubkill
	cp -f bsubkill $(LSF_BINDIR)
	chown root:root $(LSF_BINDIR)/bsubkill
	chmod u+s $(LSF_BINDIR)/bsubkill

clean:
	rm -rf bsubkill