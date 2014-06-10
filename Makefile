CC=gcc
CFLAGS=-c -Wall
LDFLAGS=

SOURCES=src/computation_tests.c
OBJECTS=$(SOURCES:.c=.o)
EXECUTABLE=computation_tests

CFLAGS += $(shell pkg-config --cflags glib-2.0)
LDFLAGS += $(shell pkg-config --libs glib-2.0)

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS)

.c.o:
	$(CC) $(CFLAGS) $< -o $@
clean:
	rm $(OBJECTS) $(EXECUTABLE)