.PHONY: build run build-dbg dbg clean

build:
	mkdir -p src/build/
	$(MAKE) -C src/ build

run: build
	./src/build/NK_PMD00

build-dbg:
	mkdir -p src/build/
	$(MAKE) -C ui/ build-dbg

dbg: build_dbg
	gdb ./src/build/NK_PMD00-dbg

clean:
	$(MAKE) -C src/ clean
