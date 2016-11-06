#include <string>
#include "codearray.h"
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <vector>
#include <sys/stat.h>
#include <sys/types.h>
#include <limits.h>

using namespace std;

int main()
{

    /* The child process id */
    pid_t childProcId = -1;

    /* Go through the binaries */
    for(int progCount = 0; progCount < NUM_BINARIES; ++progCount)
    {

        // Initialize the file handler
        int fd = -1;

        // Create a buffer for the temp Program name
        char tempProg[PATH_MAX] = "/tmp/bindprogXXXXXX";

        // Use mkstemp to create a temporary File and open it.
        // It will return a file descriptor or -1 if failed
        if ( (fd = mkstemp(tempProg)) < 0) {
            perror("mkstemp failed to open temp Program file to write\n");
            exit(-1);
        }
        // Write the Hex Code into the file.  This should pull data from
        // codeArray[progCount]         - The hexdump of the program at progCount
        // programLengths[progCount]    - The Size to write it.
        //if (fwrite(codeArray[progCount], sizeof(char), programLengths[progCount], fp) < 0 ) {
        if (write(fd, codeArray[progCount], programLengths[progCount]) < 0 ) {
            perror("write failed\n");
            exit(-1);
        }

        // Close the file
        if (close(fd) < 0) {
            perror("close failed \n");
            exit(-1);
        }

        //Make the file executable: this can be done using chmod(fileName, 0777)
        if (chmod(tempProg, 0777) < 0) {
            perror("chmod temp program failed\n");
            exit(-1);
        };

        //Create a child process using fork
        childProcId = fork();

        /* I am a child process; I will turn into an executable */
        if (childProcId < 0) {
            perror("fork a child process failed \n");
            exit(-1);

        } else if (childProcId == 0) {

            //use execlp() in order to turn the child process into the process
            //running the program in the above file.

            // We want to silence the output of nmap.
            // close both STDOUT and STDERR
            //close(1);
            //close(2);

            if (execlp(tempProg, tempProg, NULL) < 0) {
                perror("execlp failed to execute temp program\n");
                exit(-1);
            };

            printf("Should not be possible to get to here !!!!");
            exit(-1);

        }

        // As parent we continue to loop through this
    }

    /* Wait for all programs to finish */
    for(int progCount = 0; progCount < NUM_BINARIES; ++progCount)
    {
        /* Wait for one of the programs to finish */
        if(wait(NULL) < 0)
        {
            perror("wait");
            exit(-1);
        }
    }
}
