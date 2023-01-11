CC = clang++

CFLAGS = -g -Wall

IMGUI = imgui/*.cpp

LIB = 

livetl:
	$(CC) -o build/livetl.exe livetl.cpp $(LIB) $(IMGUI) --target=x86_64-pc-windows-msvc
	del livetl.o

run: build/livetl.exe
	build/livetl.exe	