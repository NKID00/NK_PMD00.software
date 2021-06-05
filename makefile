.PHONY: run build clean

build:
	mkdir -p ui/build/
	$(MAKE) -C ui/ build

run: build
	./ui/build/ui

build-debug:
	mkdir -p ui/build/
	$(MAKE) -C ui/ build-debug

debug: build_debug
	gdb ./ui/build/ui-dbg

clean:
	$(MAKE) -C ui/ clean
