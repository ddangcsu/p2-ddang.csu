import os
import sys
from subprocess import call
import os
from subprocess import Popen, PIPE

# The file name
FILE_NAME = "codearray.h";

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

    # TODO:
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

        # Use the popendemo to call HexDump
        process = Popen(CMD, stdout = PIPE)

        # Get the result into two variables output and error
        output, err = process.communicate()

        # Wait until the process completed
        wait_code = process.wait()

        # We have a success here
        if wait_code == 0:
            retVal = output

    except ValueError as msg:
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
    progCount = len(progNames)

    # The lengths of programs
    progLens = []

    # Write the array name to the header file
    headerFile.write("#include <string>\n\n")
    headerFile.write("using namespace std;\n\n")
    headerFile.write("unsigned char* codeArray[" + str(progCount) + "] = {");

    # Loop through each program
    for program in progNames:

        # Get the hexdump of each program
        hexdump = getHexDump(program)

        # If hexdump is None it means something else is wrong.  We skip
        # to the next program
        if hexdump is None:
            continue

        # Else, we will process the hexdump to get the program length
        length = len(hexdump.split(",")) - 1

        # Now we write it
        progString = "\n\nnew unsigned char[" + str(length) + "] {" + hexdump + "},"
        headerFile.write(progString)

        # Append the program Lengths
        progLens.append(length)


    # Once we done with writing all the hex we will need to close the codeArray
    headerFile.write("\n};")

    # Add array to containing program lengths to the header file
    headerFile.write("\n\nunsigned int programLengths[] = {")
    for length in progLens:
        headerFile.write("\n" + str(length) + ",")

    headerFile.write("\n};")

    # TODO: Write the number of programs.
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
    # TODO: run the g++ compiler in order to compile backbinder.cpp
    # If the compilation succeeds, print "Compilation succeeded"
    # If compilation failed, then print "Compilation failed"
    # Do not forget to add -std=gnu++11 flag to your compilation line
    GPlusPlusBinary = "/usr/bin/g++"
    global FILE_NAME

    if not os.path.exists(GPlusPlusBinary):
        print "compileFile: G++ program does not exists at " + GPlusPlusBinary
        print "\n\nCompilation failed"
        sys.exit(-1)

    if not os.path.exists(binderCppFileName):
        print "compileFile: Binder backend file not exist"
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

        # Use the popendemo to call HexDump
        process = Popen(CMD, stdout = PIPE)

        # Get the result into two variables output and error
        output, err = process.communicate()

        # Wait until the process completed
        wait_code = process.wait()

        # We have a success here
        if wait_code == 0:
            print "\n\nCompilation succeeded"
        else:
            print "\n\nCompilation failed"
    except ValueError as msg:
        print "compileFile: Popen error encountered " + msg
        print "\n\nCompilation failed"
        sys.exit(-1)


generateHeaderFile(sys.argv[1:], FILE_NAME)
compileFile("binderbackend.cpp", "bound")
