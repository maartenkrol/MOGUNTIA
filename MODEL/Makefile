#
# Make file moguntia + quickest transport:
# Tracer version used for MCF simulation!

FFILES = dimension.f90 hdf.f90 .units.f90 convection.f90 input.f90 moguntia.f90 readmet.f90 init.f90 tools.f90

CFILES = globals.c transport.c 

OBJECTS = dimension.o hdf.o units.o convection.o input.o moguntia.o globals.o transport.o readmet.o init.o tools.o 

#FFLAGS=  -O5 -c 
#FFLAGS=  -g -c 
FFLAGS = -O3 -c -fno-second-underscore
#FFLAGS = -O2 -c -YEXT_NAMES=LCS 
CFLAGS=  -O3 -c
LFLAGS=  -L/opt/local/lib/ -lmfhdf -ldf -ljpeg -lz
#LFLAGS=   -o /usr/lib64/libmfhdf.so.0 /usr/lib64/libdf.so.0

LINKER= gfortran	
FC=gfortran
CC=gcc 
MOGUNTIA : $(OBJECTS) 
	$(LINKER) $(OBJECTS) $(LFLAGS) -o $@
.f90.o: $(FFILES)
	$(FC) $(FFLAGS) $<
.c.o: $(CFILES)
	$(CC) $(CFLAGS) $<

clean:
	rm -f *.o MOGUNTIA *.mod

.SUFFIXES:
.SUFFIXES: .f90 .o .c .mod

