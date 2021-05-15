.PHONY: run build clean

build:
	mkdir -p build/
	$(MAKE) -C ui/ build

run: build
	./ui/build/ui

build_debug:
	mkdir -p build/
	$(MAKE) -C ui/ build_debug

debug: build_debug
	gdb ./ui/build/ui-dbg

clean:
	$(MAKE) -C ui/ clean
