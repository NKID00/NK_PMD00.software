CC			= gcc
CFLAGS		= -c -O3 --std=c17
CFLAGS-DBG	= -c -O0 -g --std=c17 -DDEBUG

CPPC			= g++
CPPFLAGS		= -c -O3 --std=c++17
CPPFLAGS-DBG 	= -c -O0 -g --std=c++17 -DDEBUG

LINKFLAGS		= -lgpiod -O3
LINKFLAGS-DBG	= -lgpiod -O0 -g

SQLITE3FLAGS	= -DSQLITE_THREADSAFE=0 -DSQLITE_OMIT_LOAD_EXTENSION

INFOFLAGS = -DNK_PMD00_VERSION="\"$(shell date --date=$(shell git log --pretty="%cI" -1) --utc +%-Y.%-j.)$(shell expr $(shell date --date=$(shell git log --pretty="%cI" -1) --utc +%H) "*" 3600 + $(shell date --date=$(shell git log --pretty="%cI" -1) --utc +%M) "*" 60 + $(shell date --date=$(shell git log --pretty="%cI" -1) --utc +%S))\"" \
	-DNK_PMD00_COMMIT="\"$(shell git log --pretty="%h" -1)\"" \
	-DNK_PMD00_BUILD="\"$(shell date --iso-8601=ns)\""

.PHONY: build build-dbg clean

build: build/ui

build/ui: build/ui.cpp.o build/g12864.c.o build/sqlite3.c.o
	$(CPPC) $^ $(LINKFLAGS) -o $@

build/sqlite3.c.o: sqlite3.c
	$(CC) $^ $(CFLAGS) $(SQLITE3FLAGS) -o $@

build/g12864.c.o: g12864/g12864.c
	$(CC) $^ $(CFLAGS) -o $@

build/ui.cpp.o: ui.cpp
	$(CPPC) $^ $(CPPFLAGS) $(INFOFLAGS) -o $@

build/%.c.o: %.c
	$(CC) $^ $(CFLAGS) -o $@

build/%.cpp.o: %.cpp
	$(CPPC) $^ $(CPPFLAGS) -o $@

build-debug: build/ui-dbg

build/ui-dbg: build/ui-dbg.cpp.o build/g12864-dbg.c.o build/sqlite3-dbg.c.o
	$(CPPC) $^ $(LINKFLAGS-DBG) -o $@

build/sqlite3-dbg.c.o: sqlite3.c
	$(CC) $^ $(CFLAGS-DBG) $(SQLITE3FLAGS) -o $@

build/g12864-dbg.c.o: g12864/g12864.c
	$(CC) $^ $(CFLAGS-DBG) -o $@

build/ui-dbg.cpp.o: ui.cpp
	$(CPPC) $^ $(CPPFLAGS-DBG) $(INFOFLAGS) -o $@

build/%-dbg.c.o: %.c
	$(CC) $^ $(CFLAGS-DBG) -o $@

build/%-dbg.cpp.o: %.cpp
	$(CPPC) $^ $(CPPFLAGS-DBG) -o $@

clean:
	rm -r build/
