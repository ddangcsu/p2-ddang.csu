#===============================================================================
# Script name:  binder.py
# Description:  A simple program that will read in the binary hex data
#               of a list of programs and then compile them into one large
#               executable
#===============================================================================
import os
import sys
import binascii
from subprocess import call
from subprocess import Popen, PIPE

#===============================================================================
# Generates the header file containing an array of executable codes
# @param execList - the list of executables
# @param fileName - the header file to which to write data
#===============================================================================
def generateHeaderFile(execList, fileName):

    # The header file
    headerFile = None
    progCount = 0
    progLens = ""

    # Process the list of Binaries file
    for binFile in execList:
        if not os.path.exists(binFile):
            print "generateHeaderFile: " + binFile + " does not exists"
            print "\n\ngenerateHeaderFile failed"
            sys.exit(-1)

        try:
            progSize = 0
            progSize = os.path.getsize(binFile)
        except OSError as msg:
            print "generateHeaderFile: failed get size for " + binFile
            sys.exit(-1)

        # Add up the valid program
        progCount += 1

        # Add to progLens
        progLens += str(progSize) + ","


    # Open the header file
    try:
        headerFile = open(fileName, "w")
    except IOError as msg:
        print "generateHeaderFile: open headerFile failed"
        sys.exit(-1)

    headerFile.write("#include <cstddef>\n")
    headerFile.write("\n\nusing namespace std;")

    # We only need one entries in the .h file
    # Add the programLengths array and the number of binaries
    headerFile.write("\n\nconst size_t BIN_SIZE[] = {" + progLens[:-1] + "};")
    headerFile.write("\n\n#define NUM_BINARIES " +  str(progCount))
    headerFile.close()

    return

#===============================================================================
# Compiles the combined binaries
# @param binderCppFileName - the name of the C++ binder file
# @param execName - the executable file name
#===============================================================================
def compileFile(binderCppFileName, execName):

    print("Compiling...")

    # Run the process
    # run the g++ compiler in order to compile backbinder.cpp
    # If the compilation succeeds, print "Compilation succeeded"
    # If compilation failed, then print "Compilation failed"
    # Do not forget to add -std=gnu++11 flag to your compilation line
    cppFile = binderCppFileName
    outputFile = execName

    if sys.platform == "linux" or sys.platform == "linux2":
        GPlusPlusBinary = "/usr/bin/g++"
    elif sys.platform == "win32":
        GPlusPlusBinary = "c:/MinGW/bin/g++.exe"
        cppFile = "win" + binderCppFileName

    global FILE_NAME

    if not os.path.exists(GPlusPlusBinary):
        print "compileFile: " + GPlusPlusBinary + " does not exists"
        print "\n\nCompilation failed"
        sys.exit(-1)

    if not os.path.exists(cppFile):
        print "compileFile: " + cppFile + " does not exist"
        print "\n\nCompilation failed"
        sys.exit(-1)

    if not os.path.exists(FILE_NAME):
        print "compileFile: " + FILE_NAME + " does not exist"
        print "\n\nCompilation failed"
        sys.exit(-1)

    # Build out the Command array that will be use by Popen
    CMD = [GPlusPlusBinary]                     # G++ Binary
    CMD.append('-std=gnu++11')                  # -std=gnu++11 option
    CMD.append(cppFile)                         # Binder backend cpp file
    CMD.append('-o')                            # output option
    CMD.append(outputFile)                      # The output file

    # Use Popen to get the data result
    try:

        # Use the popen to call G++ to compile the binder
        process = Popen(CMD, stdout = PIPE, stderr = PIPE)

        # Get the result into two variables output and error
        output, err = process.communicate()

        # Wait until the process completed
        wait_code = process.wait()

        # We have a success here
        if wait_code == 0:
            print "\n\nCompilation succeeded"
        else:
            print "\n\nError:" + err
            print "\n\nCompilation failed"

    except (OSError,ValueError) as msg:
        print "compileFile: Popen error encountered " + msg
        print "\n\nCompilation failed"
        sys.exit(-1)

#===============================================================================
# Function to cleanup old file before binding
#===============================================================================
def cleanupOldFiles():
    global FILE_NAME
    global OUTPUT_FILE

    if os.path.exists(FILE_NAME):
        try:
            os.remove(FILE_NAME)
        except OSError as msg:
            print "cleanupOldFiles: " + msg

    if os.path.exists(OUTPUT_FILE):
        try:
            os.remove(OUTPUT_FILE)
        except OSError as msg:
            print "cleanupOldFiles: " + msg


#===============================================================================
# Attempt another method to bind file using the copy /b trick in windows
# Currently with the hex code array, the g++ compiler in windows will give
# out of memory error and will not compile.  The new trick is to:
#  1.  Compile the binder program
#  2.  merge the files from sys.argv[1:] with the binder
#===============================================================================
def boundFiles(execList, binder):

    outFile = None
    sepString = "@DAVIDCPSC456"

    if sys.platform == "win32":
        binderFile = binder + ".exe"
    else:
        binderFile = binder

    # Append the binder file as the first file
    if not os.path.exists(binderFile):
        print "boundFiles: " + binderFile + " does not exists"
        print "\n\nBinding failed"
        sys.exit(-1)

    # Open the file for binary to append to the end of it as binary
    try:
        outFile = open(binderFile, "ab")
    except (OSError, IOError) as msg:
        print "boundFiles: Failed open to append binary data"
        sys.exit(-1)

    # Then we append the remain files from the list
    for prog in execList:
        if not os.path.exists(prog):
            print "boundFiles: " + prog + " does not exists"
            print "\n\nBinding failed"
            sys.exit(-1)

        # Open up the prog as binary for reading
        progFile = None
        try:
            progFile = open(prog, "rb")
        except (OSError, IOError) as msg:
            print "boundFiles: Failed open to read binary data"
            sys.exit(-1)

        # Write in the separator
        outFile.write(sepString)

        # Append the binary file to it
        outFile.write(progFile.read())

        # Close the progFile
        progFile.close()

    # We finally close the outFile
    outFile.close()


#===============================================================================
# Call the function here
#===============================================================================
# The file name
FILE_NAME = "codearray.h"
OUTPUT_FILE = "bound"
BINDER_BACKEND = "binderbackend.cpp"

cleanupOldFiles()
generateHeaderFile(sys.argv[1:], FILE_NAME)
compileFile(BINDER_BACKEND, OUTPUT_FILE)
boundFiles(sys.argv[1:], OUTPUT_FILE)
