SHELL = /bin/sh
CXX = g++
CPPFLAGS = -O3 -Wall

OBJECTS = ./Input_Output_Manager.o ./Apriori.o Trie.o ./Apriori_Trie.o ./main.o
CPPS = $(OBJECTS:.o=.cpp)
HPPS = $(subst .o,.hpp,$(subst main.o,,$(OBJECTS))) common.hpp


ifdef GPROF
	CPPFLAGS = -pg -fprofile-arcs -Wall
	LDFLAGS = -pg
endif

ifdef DEBUG
	CPPFLAGS = -g -fno-inline -Wall
endif


all: ../apriori

../apriori: $(OBJECTS)
	$(CXX) $^ -o ../apriori $(LDFLAGS)

%.o : %.cpp
	$(CXX) -c $(CPPFLAGS) $< -o $@

.PHONY  : doc zip bin clean
doc : 
	doxygen
zip : doc
	tar --directory=.. -cvzf ../apriori.tar.gz Documentation .apriori_config $(addprefix source/,$(CPPS)) $(addprefix source/,$(HPPS)) source/Doxyfile source/makefile
bin : ../apriori 
	tar -cvzf ../apriori_linux.tar.gz ../.apriori_config ../apriori
clean:
	rm -f $(OBJECTS) ../apriori
