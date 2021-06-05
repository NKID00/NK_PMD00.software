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

build: build/NK_PMD00

build/NK_PMD00: build/ui/main.cpp.o build/ui/ui.cpp.o build/ui/event.cpp.o \
	build/ui/g12864/g12864.c.o build/dict/ecdict.cpp.o build/dict/sqlite3.c.o
	$(CPPC) $^ $(LINKFLAGS) -o $@

build/dict/sqlite3.c.o: dict/sqlite3.c.o
	$(CC) $^ $(CFLAGS) $(SQLITE3FLAGS) -o $@

build/ui/main.cpp.o: ui/main.cpp.o
	$(CPPC) $^ $(CPPFLAGS) $(INFOFLAGS) -o $@

build/%.c.o: %.c
	$(CC) $^ $(CFLAGS) -o $@

build/%.cpp.o: %.cpp
	$(CPPC) $^ $(CPPFLAGS) -o $@

build-debug: build/NK_PMD00-dbg

build/NK_PMD00-dbg: build/ui/main.cpp.dbg.o build/ui/ui.cpp.dbg.o build/ui/event.cpp.dbg.o \
	build/ui/g12864/g12864.c.dbg.o build/dict/ecdict.cpp.dbg.o build/dict/sqlite3.c.dbg.o
	$(CPPC) $^ $(LINKFLAGS-DBG) -o $@

build/dict/sqlite3.c.dbg.o: dict/sqlite3.c
	$(CC) $^ $(CFLAGS-DBG) $(SQLITE3FLAGS) -o $@

build/ui/main.cpp.dbg.o: ui/main.cpp
	$(CPPC) $^ $(CPPFLAGS-DBG) $(INFOFLAGS) -o $@

build/%.c.dbg.o: %.c
	$(CC) $^ $(CFLAGS-DBG) -o $@

build/%.cpp.dbg.o: %.cpp
	$(CPPC) $^ $(CPPFLAGS-DBG) -o $@

clean:
	rm -r build/
