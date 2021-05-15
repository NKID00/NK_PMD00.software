.PHONY: build clean

build: build/ui.cpp.o build/g12864.c.o
	g++ $^ -lgpiod -O3 -o build/ui

build/%.c.o: %.c
	gcc $^ -c -O3 --std=c11 -o $@

build/%.cpp.o: %.cpp
	g++ $^ -c -O3 --std=c++17 -o $@

build_debug: build/ui-dbg.cpp.o build/g12864-dbg.c.o
	g++ $^ -lgpiod -O0 -g -o build/ui-dbg

build/%-dbg.c.o: %.c
	gcc $^ -c -O0 -g --std=c11 -o $@

build/%-dbg.cpp.o: %.cpp
	g++ $^ -c -O0 -g --std=c++17 -o $@

clean:
	rm -r build/
