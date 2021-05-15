.PHONY: build clean

build: build/ui.o build/g12864.o
	gcc $^ -lgpiod -O3 -o build/ui

build/%.o: %.c
	gcc $^ -c -O3 -o $@

build_debug: build/ui-dbg.o build/g12864-dbg.o
	gcc $^ -lgpiod -O0 -g -o build/ui-dbg

build/%-dbg.o: %.c
	gcc $^ -c -O0 -g -o $@

clean:
	rm -r build/
