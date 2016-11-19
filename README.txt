###############################################################################
#   Name:       David Dang
#   Email:      ddang.csu@csu.fullerton.edu
#   Language:   Python 2.7.1 and C++
#   Assignment:	2 - Binder Program
###############################################################################

###############################################################################
#  Assignment Objective
###############################################################################
Learn to implement a binder program

###############################################################################
#  Answer to Part 1 of Assignment 2
###############################################################################
I followed the instruction of part 1 on a VM of Windows 7 32 bit SP1.
The version of 7-zip is 16.04

My files:
    firework.gif    - a downloaded animated gif of the firework
    worm.7z         - a 7zip version of the worm.bat program

The command that I issued was: copy /b firework.gif + worm.7z result

1.  The above copy command use the /b option to treat all the source input
files as binary and combine or concatenate them together into the result
file.  This effectively allow us to hide file or files behind an image.

###
### Test case 1: renamed the result file to result.7z
###
I tried to open the result.7z file with the 7-zip file manager, then
attempted to extract the result.7z file, I received an error:
      "Can not open the file as [7z] archive"

However, when I right clicked on result.7z, chose 7-zip -> chose the
second Open Archive -> 7z option, I was able to extract the worm.bat file.

###
### Test case 2: renamed the result file to result.gif
###
I was able to open and view the firework animation without any problem.

From the above experiment, I believe that every file has the following
metadata structure:
File Header       - Indicated the type or signature of the file
File Data or Body - The body data for this file
File Footer       - The ending mark of the file

When a program in windows try to open a file such as 7zip, it will read
and parse the file header to determine whether the signature and structure
is valid.  If it is, it will read in the full file and open it.

This kind of follow the experiment as the file signature of result should
be a GIF file.  Hence I was able to open it without error when the file
extension is GIF.  However, when I renamed it to 7z, I was not able to
open as the header file signature is not 7z but was GIF.

One reason that I think the second option which I force 7zip to open the
archive as 7z work is because 7zip program actually scan the file until
it see the signature of the 7z file type, and then reading the remain
data from the file to allow the file to extract.

2.  Users and hackers can definitely use this technique to hide malicious
codes by binding the malicious code (i.e worm.7z) after a valid, harmless
looking program or data file (i.e. firework.gif). From the user view, the
file is just another image file and open just like any other image file.
Yet it actually carry a hidden payload that only the one implanted would
know.

3.  Surprisingly that this technique is working out quite well in term
of avoiding detection by anti-virus tools.  As a test, I did the following:

  a)  Turn off antivirus on my Windows 7 VM so that it won't prevent me
      from creating the malicious file

  b)  Create a test file called malware.com that contain the EICAR test.
      This string is harmless even if run on a machine.
      X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*

  c)  Use 7-zip to create an archive of this file called malware.7z

  d)  Perform the technique to hide my malicious malware behind a gif:
      copy /b firework.gif + malware.7z malware.gif

  e)  Activate the local AntiVirus and scan both files:
        malware.7z    - Detected as Malicious ! YAY
        malware.gif   - No threat detected, file is clean :(

  g)  Submit both files to virustotal.com to scan against multiple engine:
        malware.7z    - Detected as malicious 38/52 Antivirus Engines
        https://virustotal.com/en/file/8ebb47aa018c441bad59e0e734f97d8f5e406dcbde0eac39d4329d8014597da9/analysis/

        malware.gif   - Detected as malicious 4/53 Antivirus Engines
        https://virustotal.com/en/file/690afd07139e0985bd0bf23a272002f0c0f586830277a5cb41dd3a31aca5ea01/analysis/1478715718/

This may not be a thorough test, but I think it quite clear that this
technique is quite nice to hide malicious codes and avoid detection.


###############################################################################
#  Part 2 Document Sections
###############################################################################
1.  Assumption
2.  Observation
3.  Bonus
4.  Directory structures
5.  Program run instruction
6.  Assignment Analysis
7.  Credit/Source

###############################################################################
#  Assumption
###############################################################################

This assignment assumed that the system already have g++ 4.8 installed as it
is required to compile the bound programs

Linux Version:
    a) Python 2.7.x installed
    b) g++ 4.8 installed

Windows Version:
    a) Python 2.7.x installed and added to PATH environment variable

    b) MinGW with g++ for Windows installed
       http://www.mingw.org/
       The path of the g++ must be in c:/MinGW/bin/g++.exe
       Path c:/MinGW/bin must be added in the PATH environment variable

NOTE:  The bound method with merging binaries relied on a separator marker.
I put in "@DAVIDCPSC456" as a separator. If any binaries that coincidentally contain
that string in the exact format, then the bound program may break as it split
the binary incorrectly.

###############################################################################
#  Observation
###############################################################################

This binder assignment is interesting as it gives a glimpse into how programs
can be bound together and able to execute all of them.  Another observation is
that the assignment binder relied on a compiler to actually compile the bound
programs.  If the binder was to perform all this tasks, a lot more effort may
be needed in order to construct the machine code for it.

While testing multiple system with the byte code array method, the g++ compiler
will always throw an out of memory error when the codearray.h file get large
(about 10MB or more).  I ended up re-write the program using the binary file
merge method similar to that of Part 1 of this assignment as way to bound the
list of programs.  Then write the logic to parse the binary file byte for byte
to split the binary base on a separator to re-construct the binary file before
running it with fork().

###############################################################################
#  Bonus
###############################################################################

I implement the bonus program to run on a windows machine.  See the prerequisite
in the Assumption section.

In windows, I also experienced the g++ compiler out of memory issue with byte
code array header file.  Changed it to binary merge method and its working now.
Relied on CreateProcess in windows to replace fork() code.

A couple limitations:
  1) The program is limited to only binding .exe binaries.
  2) The program does not run binaries that has dependencies (i.e. notepad.exe)

###############################################################################
# Directory structures
###############################################################################
We assume that all files will be extracted/untar into a certain /<path>.
The directory tree should be as follow:

/<path>/p2-ddang.csu
        |-- README.txt                  - This README file
        |-- result.gif                  - Part 1 result file
        |-- binder.py                   - The binder program
        |-- binderbackend.cpp           - The Linux CPP support backend
        |-- winbinderbackend.cpp        - The Windows CPP support backend

The following are file created after the running the binder program:

/<path>/p2-ddang.csu
  |-- codearray.h                       - The generated CPP header file
  |-- bound/bound.exe (windows)         - The binary of the bound program

###############################################################################
# Program Run instruction
###############################################################################

1. Open a terminal and change directory to the program path
    cd /<path>/p2-ddang.csu

2. To run the binder program:
    python binder.py <prog1> <prog2>...

    Example of combine three binary together into a single file called bound
    python binder.py /bin/ls /bin/date /bin/ps

To run the bonus version:

1.  Open a command prompt windows and change directory to the path

2.  To run the binder program:
    python binder.py <prog1> <prog2>...

###############################################################################
# Assignment Analysis
###############################################################################
This assignment helps to provide hand on understanding of how binder work.
Initially the byte code array method was simple and straight forward.  However,
for some odd reason I keep getting g++ out of memory error issue when tested
with larger binaries in both Linux and Windows.

Used the knowledge learned in Part 1 was able to help remedy the program by
merging all the binaries after the bound program and then split it back out again
using a separator marker to run it.

###############################################################################
# Credit/Source
###############################################################################
While working on this assignment I used some information/howto from various
sources to help with the code in the assignment.

- samples code provided with the assignment

- virustotal.com website for testing virus detection for part 1
- www.eicar.org website for the sample malware test file

- MSDN for information on CreateProcess and sample CreateProcess code:
https://msdn.microsoft.com/en-us/library/windows/desktop/ms682512(v=vs.85).aspx
