#===============================================================================
# Script name:  binder.py
# Description:  A simple program that will read in the binary hex data
#               of a list of programs and then compile them into one large
#               executable
#===============================================================================
import os
import sys
from subprocess import call
from subprocess import Popen, PIPE

#===============================================================================
# Returns the hexidecimal dump of a particular binary file
# @execPath - the executable path
# @return - returns the hexidecimal string representing
# the bytes of the program. The string has format:
# byte1,byte2,byte3....byten,
# For example, 0x19,0x12,0x45,0xda,
#===============================================================================
def getHexDump(execPath):

    # The return value
    retVal = None
    HexDumpBinary = "/usr/bin/hexdump"

    # Check if execPath actually exists
    if not os.path.exists(execPath):
        print "getHexDump: Path <" + execPath + "> does not exists !"
        return retVal

    # Check to make sure that the HexDump Binary exists
    if not os.path.exists(HexDumpBinary):
        print "getHexDump: Binary <" + HexDumpBinary + "> does not exist !"
        sys.exit(-1)

    # 1. Use popen() in order to run hexdump and grab the hexadecimal bytes of the program.
    # 2. If hexdump ran successfully, return the string retrieved. Otherwise, return None.
    # The command for hexdump to return the list of bytes in the program in C++ byte format
    # the command is hexdump -v -e '"0x" 1/1 "%02X" ","' progName

    # Build out the Command array that will be use by Popen
    CMD = [HexDumpBinary]                       # Hex Dump Binary
    CMD.append('-v')                            # Display all input data
    CMD.append('-e')                            # Format string option
    CMD.append('''"0x" 1/1 "%02X" ","''')       # The actual format string
    CMD.append(execPath)                        # The file to get hex dump

    # Use Popen to get the data result
    try:

        # Create a process using popen
        process = Popen(CMD, stdout = PIPE, stderr = PIPE)

        # Get the result into two variables output and error
        output, err = process.communicate()

        # Wait until the process completed
        wait_code = process.wait()

        # We have a success here pass the output of HEX back to retVal
        if wait_code == 0:
            retVal = output
        else:
            print "Process has error: " + err
            retVal = None

    except (OSError, ValueError) as msg:
        print "getHexDump: Popen error encountered " + msg
        sys.exit(-1)

    return retVal

#===============================================================================
# Generates the header file containing an array of executable codes
# @param execList - the list of executables
# @param fileName - the header file to which to write data
#===============================================================================
def generateHeaderFile(execList, fileName):

    # The header file
    headerFile = None

    # Open the header file
    try:
        headerFile = open(fileName, "w")
    except IOError as msg:
        print "generateHeaderFile: open headerFile failed"
        sys.exit(-1)

    # The program array
    progNames = execList

    # Number of programs to bind
    progCount = 0

    # The lengths of programs
    progLens = []

    # Write the array name to the header file
    headerFile.write("#include <string>\n\n")
    headerFile.write("using namespace std;\n\n")
    headerFile.write("unsigned char* codeArray[] = {\n");

    # Loop through each program
    for program in progNames:

        # Get the hexdump of each program
        hexdump = getHexDump(program)

        # If hexdump is None it means something else is wrong.  We skip
        # to the next program
        if hexdump is None:
            continue

        # Else, we will process the hexdump to get the program length
        # We substract one because of the extra comma in hex
        progLen = str(len(hexdump.split(",")) - 1)

        # Now we write it
        progString = "\nnew unsigned char[" + progLen + "] {" + hexdump + "},"
        headerFile.write(progString)

        # Append the program Lengths
        progLens.append(progLen)


    # Once we done with writing all the hex we will need to close the codeArray
    headerFile.write("\n};")

    # Combine the progLens into a string separate by comma
    length = ",".join(progLens)

    # Get the final Program Count that we wrote
    progCount = len(progLens)

    # Add array to containing program lengths to the header file
    headerFile.write("\n\nunsigned int programLengths[] = {" + length + "};")

    # Write the number of programs.
    headerFile.write("\n\n#define NUM_BINARIES " +  str(progCount))

    # Close the header file
    headerFile.close()


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

    GPlusPlusBinary = "/usr/bin/g++"
    global FILE_NAME

    if not os.path.exists(GPlusPlusBinary):
        print "compileFile: " + GPlusPlusBinary + " does not exists"
        print "\n\nCompilation failed"
        sys.exit(-1)

    if not os.path.exists(binderCppFileName):
        print "compileFile: " + binderCppFileName + " does not exist"
        print "\n\nCompilation failed"
        sys.exit(-1)

    if not os.path.exists(FILE_NAME):
        print "compileFile: " + FILE_NAME + " does not exist"
        print "\n\nCompilation failed"
        sys.exit(-1)

    # Build out the Command array that will be use by Popen
    CMD = [GPlusPlusBinary]                     # G++ Binary
    CMD.append('-std=gnu++11')                  # -std=gnu++11 option
    CMD.append(binderCppFileName)               # Binder backend cpp file
    CMD.append('-o')                            # output option
    CMD.append(execName)                        # The output file

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
# Call the function here
#===============================================================================
def cleanupOldFiles(None):
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
# Call the function here
#===============================================================================
# The file name
FILE_NAME = "codearray.h"
OUTPUT_FILE = "bound"
BINDER_BACKEND = "binderbackend.cpp"

cleanupOldFiles()
generateHeaderFile(sys.argv[1:], FILE_NAME)
compileFile(BINDER_BACKEND, OUTPUT_FILE)
