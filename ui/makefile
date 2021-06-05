.PHONY: build clean

build: build/ui.cpp.o build/g12864.c.o build/sqlite3.c.o
	g++ $^ -lgpiod -O3 -o build/ui

build/sqlite3.c.o: sqlite3.c
	gcc $^ -c -O3 --std=c11 -DSQLITE_THREADSAFE=0 -DSQLITE_OMIT_LOAD_EXTENSION -o $@

build/g12864.c.o: g12864/g12864.c
	gcc $^ -c -O3 --std=c11 -o $@

build/%.c.o: %.c
	gcc $^ -c -O3 --std=c11 -o $@

build/%.cpp.o: %.cpp
	g++ $^ -c -O3 --std=c++17 -o $@

build_debug: build/ui-dbg.cpp.o build/g12864-dbg.c.o build/sqlite3-dbg.c.o
	g++ $^ -lgpiod -O0 -g -o build/ui-dbg

build/sqlite3-dbg.c.o: sqlite3.c
	gcc $^ -c -O0 -g --std=c11 -DSQLITE_THREADSAFE=0 -DSQLITE_OMIT_LOAD_EXTENSION -o $@

build/g12864-dbg.c.o: g12864/g12864.c
	gcc $^ -c -O0 -g --std=c11 -o $@

build/%-dbg.c.o: %.c
	gcc $^ -c -O0 -g --std=c11 -o $@

build/%-dbg.cpp.o: %.cpp
	g++ $^ -c -O0 -g --std=c++17 -o $@

clean:
	rm -r build/
