./ui/build/%.o: ./ui/%.c
    gcc -c %< -o %@ 

./ui/build/ui: ./ui/build/ui.o ./ui/build/g12864.o
    gcc %< -o %@

.PHONY: run build clean

build: ./ui/build/ui

run: build
    ./ui/build/ui

clean:
    rm -r build/