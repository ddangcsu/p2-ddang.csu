#include <windows.h>
#include <tchar.h>
#include "codearray.h"
#include <stdlib.h>
#include <stdio.h>

using namespace std;

int main()
{

    /* Array used by CreateProcess */
    STARTUPINFO si[NUM_BINARIES];
    PROCESS_INFORMATION pi[NUM_BINARIES];

    /* Array to hold the Handle */
    HANDLE handles[NUM_BINARIES];

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
    DWORD dwRetVal = 0;  // Used for GetTempPath

    dwRetVal = GetTempPath(MAX_PATH, tempPath);

    if (dwRetVal > MAX_PATH || dwRetVal == 0) {
        printf ("GetTempPath failed\n");
        return -1;
    }

    /* Go through the binaries */
    for(int progCount = 0; progCount < NUM_BINARIES; ++progCount)
    {
        /* Get a Temp File Name */
        TCHAR tempProg[MAX_PATH] = {0};
        TCHAR currentPath[MAX_PATH] = {0};

        if (GetTempFileName(tempPath, TEXT("bind"), 0, tempProg) == 0)
        {
            printf("GetTempFileName failed \n");
            return -1;
        }

        if (GetCurrentDirectory(sizeof(currentPath), currentPath) == 0)
        {
            printf("GetCurrentDirectory failed\n");
            return -1;
        }
        // Append the extension of .exe to the tempProg
        strncat(tempProg, ".exe", 5);

        /* Open the file to write the hex code */
        FILE* fp = fopen(tempProg, "wb");

        if (!fp) {
            printf ("fopen failed \n");
            return -1;
        }

        // Write the Hex Code into the file.  This should pull data from
        // codeArray[progCount]         - The hexdump of the program at progCount
        // programLengths[progCount]    - The Size to write it.
        if (fwrite(codeArray[progCount], sizeof(char), programLengths[progCount], fp) < 0 ) {
            perror("fwrite failed\n");
            exit(-1);
        }

        /* Close file */
        fclose(fp);

        /* Create a process to run the file */
        if (! CreateProcess(
                NULL,
                tempProg,
                NULL,
                NULL,
                FALSE,
                0,
                NULL,
                currentPath,
                &si[progCount],
                &pi[progCount]) )
        {
            printf("CreateProcess for %s failed %d.\n", tempProg, GetLastError());
            return -1;
        }

        /* Save off the process handle into handles array */
        handles[progCount] = pi[progCount].hProcess;
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
