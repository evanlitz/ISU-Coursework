
// Name: Evan Litzer
// Modified the file so that it counts digits. Did this by declaring an integer 'd' and initalizing it to 0 before
// checking the buffer string for characters 1-9 and counting them, before displaying it as the fourth value as instructed in the directions.
// Comments for changes are included.

#include "kernel/types.h"
#include "kernel/stat.h"
#include "kernel/fcntl.h"
#include "user/user.h"

char buf[512];

void
wc(int fd, char *name)
{
  int i, n;
  // Declaring an integer 'd' that tracks the amount of numbers between range 1-9
  int l, w, c, d, inword;
  // Initializing the integer 'd' as 0
  l = w = c = d = 0;
  inword = 0;
  while((n = read(fd, buf, sizeof(buf))) > 0){
    for(i=0; i<n; i++){
      c++;
      // This checks the buffer string input for integer values that are bigger than or equal to 0 and smaller than or equal to 9
      // If the buffer character is found to be in the range, then the 'd' integer sum is incremented.
      if(buf[i] >= '0' && buf[i] <= '9')
      {
        d++;
      }
      if(buf[i] == '\n')
        l++;
      if(strchr(" \r\t\n\v", buf[i]))
        inword = 0;
      else if(!inword){
        w++;
        inword = 1;
      }
    }
  }
  if(n < 0){
    printf("wc: read error\n");
    exit(1);
  }
  // I changed the printf statement to include the 'd' integer count.
  printf("%d %d %d %d %s\n", l, w, c, d, name);

}

int
main(int argc, char *argv[])
{
  int fd, i;

  if(argc <= 1){
    wc(0, "");
    exit(0);
  }

  for(i = 1; i < argc; i++){
    if((fd = open(argv[i], O_RDONLY)) < 0){
      printf("wc: cannot open %s\n", argv[i]);
      exit(1);
    }
    wc(fd, argv[i]);
    close(fd);
  }
  exit(0);
}
