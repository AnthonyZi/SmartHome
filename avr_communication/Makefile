BUILD=devel
CC := gcc


ifeq ($(BUILD),devel)
FLAGS := -g -Wall
else
FLAGS := -O3
endif

CFILES=avr_transmitter.c test.c printhelp.c avr_receiver.c
HFILES=avr_transmitter.h printhelp.h avr_receiver.h

all: $(CFILES) $(HFILES)
	$(CC) $(FLAGS) -o test $(CFILES)

clean:
	rm *.o test
