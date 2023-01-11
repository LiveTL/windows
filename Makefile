CC = clang++

CFLAGS = -g -Wall

IMGUI = imgui/imgui.cpp imgui/imgui_demo.cpp imgui/imgui_draw.cpp imgui/imgui_impl_dx11.cpp imgui/imgui_impl_win32.cpp imgui/imgui_stdlib.cpp imgui/imgui_tables.cpp imgui/imgui_widgets.cpp

LIB = 

livetl:
	$(CC) -o build/livetl.exe livetl.cpp $(LIB) $(IMGUI) --target=x86_64-pc-windows-msvc
	del livetl.o

run: build/livetl.exe
	build/livetl.exe	