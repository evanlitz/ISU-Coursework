CC = gcc
CFLAGS = -Wall -Werror

all: dungeon

dungeon: dungeon.c
	$(CC) $(CFLAGS) dungeon.c -o dungeon -lncurses

clean:
	rm -rf dungeon