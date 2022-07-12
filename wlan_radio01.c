#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <string.h>

#define UART_LEN 254

int main(int argc, char ** argv) 
{
  int fd;
  // Open the Port. We want read/write, no "controlling tty" status, and open it no matter what state DCD is in
  fd = open("/dev/ttyAMA0", O_RDWR | O_NOCTTY | O_NDELAY);
  if (fd == -1) {
    perror("open_port: Unable to open /dev/ttyAMA0 - ");
    return(-1);
  }

  // Turn off blocking for reads, use (fd, F_SETFL, FNDELAY) if you want that
  fcntl(fd, F_SETFL, 0);

  // Write to the port
	//system("mpc clear");
	//system("mpc load radiosender");
	system("mpc play");
  
	int n = 0;
	int buf_count = 0;
	char b = '0';
	char buf[256];
	int i = 0;
	FILE *fp;
	char line[UART_LEN];

	typedef enum {READ_CHAR, WRITE_IN_BUFFER, TERMINATE, COMPARE} state_t;
	state_t state = READ_CHAR;
	
	while (1)
	{
		switch (state)
		{
			case READ_CHAR:
				n = read(fd, &b, 1);
				if (n <= 0) state = READ_CHAR;
				//printf("%c\t%x\n",b,b);
				if (b == '\n') //LF 0x0A
				{
					state = TERMINATE;
					break;
				}
				if (buf_count != 255) state = WRITE_IN_BUFFER;
				else 
				{
					buf_count = 0;
					state = READ_CHAR;
				}
			break;
			case WRITE_IN_BUFFER:
				//printf("WRITE_IN_BUFFER\n");
				buf[buf_count] = b;
				buf_count++;
				state = READ_CHAR;
			break;
			case TERMINATE:
				//printf("TERMINATE\n");
				buf[buf_count] = '\0';
				buf_count = 0;
				state = COMPARE;
			break;
			case COMPARE:
				//printf("Ausgabe:\t%s\n",buf);

				for (i = 0; i < UART_LEN; i++) line[i]=' ';
				if (!strcmp(buf, "NEXT_BUTTON"))
				{
					system("mpc next");
					system("mpc play");
								/* line of easa!from unix command*/
					fp = popen("mpc current", "r");		/* Issue the command.		*/
									/* Read a line			*/
					while ( fgets( line, sizeof line, fp))
					{
						printf("--- %s", line);
						write(fd,"1",1);
						write(fd,line,UART_LEN);
						write(fd,"\n",1);
					}
					pclose(fp);
				}
				if (!strcmp(buf, "PREV_BUTTON"))
				{
					system("mpc prev");
					system("mpc play");
					fp = popen("mpc current", "r");		/* Issue the command.		*/
									/* Read a line			*/
					while ( fgets( line, sizeof line, fp))
					{
						printf("--- %s", line);
						write(fd,"1",1);
						write(fd,line,UART_LEN);
						write(fd,"\n",1);
					}
					pclose(fp);
				}
				if (!strcmp(buf, "CURRENT"))
				{
					fp = popen("mpc current", "r");		/* Issue the command.		*/
									/* Read a line			*/
					while ( fgets( line, sizeof line, fp))
					{
						printf("--- %s", line);
						write(fd,"1",1);
						write(fd,line,UART_LEN);
						write(fd,"\n",1);
					}
					pclose(fp);
				}
				if (!strcmp(buf, "PLAY_BUTTON"))
				{
					system("mpc toggle");
				}
				state = READ_CHAR;
			break;
		}
	}

  close(fd);
  return 0;
}