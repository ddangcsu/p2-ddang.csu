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
# Returns the hexidecimal dump of a particular binary file
# @execPath - the executable path
# @return - returns the hexidecimal string representing
# the bytes of the program. The string has format:
# byte1,byte2,byte3....byten,
# For example, 0x19,0x12,0x45,0xda,
#===============================================================================
def getHexDump(execPath):

    inFile = None
    hexContent = None
    hexString = ''

    # Check if execPath actually exists
    if not os.path.exists(execPath):
        print "getHexDump2: Path <" + execPath + "> does not exists !"
        return retVal

    try:
        # Open the file for binary read
        inFile = open(execPath, "rb")
    except (OSError, IOError) as msg:
        print "getHexDump2: Failed open to read binary data"
        sys.exit(-1)

    # Read in the binary file and use binascii to convert to hex
    try:
        hexContent = binascii.b2a_hex(inFile.read())
    except (binascii.Error, binascii.Incomplete) as msg:
        print "getHexDump2: Failed to convert data to hex string"
        sys.exit(-1)

    # Close the file
    inFile.close()

    # Check to see if we should continue to format the string
    if (len(hexContent) == 0):
        return retVal;

    # Loop through the hexContent and step through each byte to build the
    # C++ byte which is 0xNN, using list slicing index:index + 2
    for index in range (0, len(hexContent), 2):
        hexString += '0x' + hexContent[index:index+2] + ','

    return hexString

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
# Call the function here
#===============================================================================
# The file name
FILE_NAME = "codearray.h"
OUTPUT_FILE = "bound"
BINDER_BACKEND = "binderbackend.cpp"

cleanupOldFiles()
generateHeaderFile(sys.argv[1:], FILE_NAME)
compileFile(BINDER_BACKEND, OUTPUT_FILE)
