#include "codearray.h"
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <limits.h>
#include <string.h>

using namespace std;

void runChild(char* progName) {

    //Make the file executable: this can be done using chmod(fileName, 0777)
    if (chmod(progName, 0777) < 0) {
        perror("chmod temp program failed\n");
        exit(-1);
    };

    //Create a child process using fork
    pid_t childProcId = fork();

    /* I am a child process; I will turn into an executable */
    if (childProcId < 0) {
        perror("fork a child process failed \n");
        exit(-1);

    } else if (childProcId == 0) {

        if (execlp(progName, progName, NULL) < 0) {
            perror("execlp failed to execute temp program\n");
            exit(-1);
        };

        printf("Should not be possible to get to here !!!!");
        exit(-1);

    }

}


int main(int argc, char** argv)
{

    /* Variables for parsing the binary bound.exe file */
    char sepBytes[6] = "DAVID";
    char binFile[PATH_MAX] = {0};
    char progName[PATH_MAX] = {0};
    size_t progSize = 0;
    int progRun = 0;
    int progCount = 0;

    int fdOut = -1;

    // Create a buffer for the temp Program name
    char tempProg[PATH_MAX] = {0};

    /* Get the bound binary file */
    strncpy(binFile, argv[0], PATH_MAX);

    /* Open the binary file */
    FILE *fd = fopen(binFile, "rb");
    if (!fd) {
        printf ("Error fopen failed to open %s\n", binFile);
        exit(-1);
    }

    /* Loop through to read the binary file until EOF */
    while (!feof(fd)) {
        char aByte;
        fpos_t posAfterRead;

        /* Read 1 byte at a time */
        if ( fread(&aByte, sizeof(char), sizeof(aByte), fd) < 0 ) {
            printf ("fread failed \n");
            exit(-1);
        }

        /* Get current file marker */
        if (fgetpos(fd, &posAfterRead) < 0) {
            printf("fgetpos failed\n");
            exit(-1);
        }

        /* We reached the end of file.  Do not write the last byte */
        if (feof(fd)) {
            continue;
        }

        /* Check if we get marker */
        if (memcmp(&aByte, &sepBytes, sizeof(char)) == 0) {
            /* May have a match, lets peek ahead 4 bytes */
            char seperator[5] = {0};

            if ( fread(seperator, sizeof(char), 4, fd) < 0) {
                printf ("fread peeking failed \n");
                exit(-1);
            }

            /* See if we got seperator */
            if ( memcmp(&sepBytes[1], &seperator, 4) == 0) {

                /* Proces when not the bound.exe file*/
                if (progCount > 0 && progCount <= NUM_BINARIES) {
                    /* Because our actual program is after the bound program */
                    int index = progCount - 1;

                    /* Close the temp file */
                    if (close(fdOut) < 0) {
                        printf("close fdOut failed\n");
                    }
                    if (progSize == BIN_SIZE[index]) {
                        runChild(tempProg);
                        progRun += 1;
                    } else {
                        printf("File size mismatched, ignored running\n");
                    }
                }

                /* Increment by 1 */
                progCount += 1;
                strncpy(tempProg,"/tmp/bindXXXXXX", PATH_MAX);
                /* Create a new file name */
                if ( (fdOut = mkstemp(tempProg)) < 0) {
                    perror("mkstemp failed to open temp Program file to write\n");
                    exit(-1);
                }

                /* Reset progSize */
                progSize = 0;

                /* We continue the loop */
                continue;

            } else {
                /* Not a separator, reset position of file */
                fsetpos(fd, &posAfterRead);
            }

        }

        /* We only writing when the program is the 2nd and + */
        if (progCount > 0 && progCount <= NUM_BINARIES) {
            if (write(fdOut, &aByte, sizeof(char)) < 0) {
                printf("write failed \n");
                exit(-1);
            }
            progSize += 1;
        }

    } // End while loop to read binary file

    /* We close the binary file */
    fclose(fd);

    /* We need to run the final file */
    if (progCount > 0 && progCount <= NUM_BINARIES) {
        /* Because the progCount is after bound program */
        int index = progCount - 1;
        /* Close the temp file */
        if (close(fdOut) < 0) {
            printf("close fdOut failed\n");
        }
        if (progSize == BIN_SIZE[index]) {
            runChild(tempProg);
            progRun += 1;
        } else {
            printf("file size mismatch.  Not running program \n");
        }
    }

    /* Wait for all programs to finish only if progCount > 0*/
    for(int children = 0; children < progRun; ++children)
    {
        /* Wait for one of the programs to finish */
        if(wait(NULL) < 0)
        {
            perror("wait");
            exit(-1);
        }
    }

    return 0;
}
