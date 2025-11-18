OBJDIR = objs
BINDIR = .

SRCS = main.c input.c output.c debug.c
OBJS = $(OBJDIR)/main.o $(OBJDIR)/input.o $(OBJDIR)/output.o $(OBJDIR)/debug.o
HDRS = defines.h structs.h maindefs.h
EXE_FILE = $(BINDIR)/tsl
LIBS =

CC = gcc

default:
	@echo 
	@echo   Make options:
	@echo
	@echo   build:   build tsl tool 
	@echo 

build: begin $(EXE_FILE) end

begin:
	@echo "Building tsl..."
end:
	@echo "Building tsl is completed"

$(EXE_FILE): $(SRCS) $(HDRS)
	$(CC) -c -o $(OBJDIR)/main.o main.c
	$(CC) -c -o $(OBJDIR)/input.o input.c
	$(CC) -c -o $(OBJDIR)/output.o output.c
	$(CC) -c -o $(OBJDIR)/debug.o debug.c
	$(CC) -o $(EXE_FILE) $(OBJS) $(LIBS)

clean:
	rm $(BINDIR)/tsl

realclean:
	rm $(BINDIR)/tsl objs/*.o

