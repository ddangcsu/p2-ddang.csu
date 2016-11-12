#include <windows.h>
#include <tchar.h>
#include "codearray.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

using namespace std;

void runChild(TCHAR *fileName, int progCount, STARTUPINFO si[], PROCESS_INFORMATION pi[], HANDLE handle[])
{
    /* Create a process to run the file */
    if (! CreateProcess(
            NULL,
            fileName,
            NULL,
            NULL,
            FALSE,
            0,
            NULL,
            NULL,
            &si[progCount],
            &pi[progCount]) )
    {
        printf("CreateProcess for %s failed %d.\n", fileName, GetLastError());
        exit(-1);
    }

    /* Save off the process handle into handles array */
    handle[progCount] = pi[progCount].hProcess;

}

int main(int argc, char** argv)
{
    /* Variables for parsing the binary bound.exe file */
    char sepBytes[6] = "DAVID";
    char binFile[MAX_PATH] = {0};
    char progName[MAX_PATH] = {0};
    int progCount = 0;

    /* Array used by CreateProcess */
    STARTUPINFO si[NUM_BINARIES];
    PROCESS_INFORMATION pi[NUM_BINARIES];

    /* Array to hold the Handle */
    HANDLE handles[NUM_BINARIES];


    /* File handler for temp file */
    FILE *fdOut;

    /* Get the bound.exe binary file */
    strncpy(binFile, argv[0], MAX_PATH);
    unsigned int fileLen = strlen(binFile);
    char extension[5] = ".exe";

    /* Attempt to add .exe to the file if user run it without .exe */
    if (fileLen < 5 || (memcmp( &binFile[fileLen - 4], &extension, 4)) != 0 ) {
        strncat(binFile, extension, 5);
    }

    /* Initialize each of them */
    for (int i = 0; i < NUM_BINARIES; i++) {
        /* Initialize si */
        ZeroMemory ( &si[i], sizeof(si[i]) );
        si[i].cb = sizeof (si[i]);

        /* Initialize pi */
        ZeroMemory ( &pi[i], sizeof(pi[i]) );

        /* Initialize handler */
        ZeroMemory ( &handles[i], sizeof(handles[i]) );
    }

    /* Retrieve the tempPath */
    TCHAR tempPath[MAX_PATH] = {0};
    TCHAR tempProg[MAX_PATH] = {0};
    DWORD dwRetVal = 0;  // Used for GetTempPath

    dwRetVal = GetTempPath(MAX_PATH, tempPath);

    if (dwRetVal > MAX_PATH || dwRetVal == 0) {
        printf ("GetTempPath failed\n");
        return -1;
    }

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
                    fclose(fdOut);
                    int index = progCount - 1;
                    runChild(tempProg, index, si, pi, handles);
                }

                /* Increment by 1 */
                progCount += 1;
                /* Create a new file name */
                if (GetTempFileName(tempPath, TEXT("bind"), 0, tempProg) == 0) {
                    printf("GetTempFileName failed \n");
                    return -1;
                }

                // Append the extension of .exe to the tempProg
                strncat(tempProg, ".exe", 5);
                fdOut = fopen(tempProg, "wb");
                if (!fdOut) {
                    printf ("fopen failed to open %s\n", tempProg);
                    exit(-1);
                }

                /* We continue the loop */
                continue;

            } else {
                /* Not a separator, reset position of file */
                fsetpos(fd, &posAfterRead);
            }

        }

        /* We only writing when the program is the 2nd and + */
        if (progCount > 0 && progCount <= NUM_BINARIES) {
            if (fwrite(&aByte, sizeof(char), sizeof(aByte), fdOut) < 0) {
                printf("fwrite failed \n");
                exit(-1);
            }
        }

    } // End while loop to read binary file

    /* We close the binary file */
    fclose(fd);

    /* We need to run the final file */
    if (progCount > 0 && progCount <= NUM_BINARIES) {
        fclose(fdOut);
        int index = progCount - 1;
        runChild(tempProg, index, si, pi, handles);
    }

    /* Wait for all programs to finish */
    DWORD retVal = WaitForMultipleObjects(NUM_BINARIES, handles, TRUE, INFINITE);

    if (retVal != WAIT_OBJECT_0) {
        printf("WaitForMultipleObjects failed\n");
    }

    for (int i = 0; i < NUM_BINARIES; i++) {
        CloseHandle(pi[i].hProcess);
        CloseHandle(pi[i].hThread);
    }

    return 0;
}
