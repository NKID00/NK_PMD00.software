.PHONY: build run build-debug debug clean

build:
	mkdir -p src/build/
	$(MAKE) -C src/ build

run: build
	./src/build/NK_PMD00

build-debug:
	mkdir -p src/build/
	$(MAKE) -C ui/ build-debug

debug: build_debug
	gdb ./src/build/NK_PMD00-dbg

clean:
	$(MAKE) -C src/ clean
