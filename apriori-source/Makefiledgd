# use the following way: make -f Makefile upload
include makefile
.PHONY  : upload
upload : doc zip bin
	scp -r ../Documentation sziami.cs.bme.hu:public_html/en/apriori
	scp ../apriori.tar.gz sziami.cs.bme.hu:public_html/en/apriori
	scp ../apriori_linux.tar.gz sziami.cs.bme.hu:public_html/en/apriori/binaries/Linux
	cvs commit
