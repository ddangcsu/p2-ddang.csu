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

###############################################################################
#  Observation
###############################################################################

This binder assignment is interesting as it gives a glimpse into how programs
can be bound together and able to execute all of them.  Another observation is
that the assignment binder relied on a compiler to actually compile the bound
programs.  If the binder was to perform all this tasks, a lot more effort may
be needed in order to construct the machine code for it.

###############################################################################
#  Bonus
###############################################################################

TBD

###############################################################################
# Directory structures
###############################################################################
We assume that all files will be extracted/untar into a certain /<path>.
The directory tree should be as follow:

/<path>/p2-ddang.csu
        |-- README.txt                  - This README file
        |-- binder.py                   - The binder program
        |-- binderbackend.cpp           - The CPP support backend
        |-- bonus/                      - bonus program
            |-- TBD


The following are file created after the running the binder program:

/<path>/p2-ddang.csu
  |-- codearray.h                       - The generated CPP header file
  |-- bound                             - The binary of the bound program

###############################################################################
# Program Run instruction
###############################################################################

1. Open a terminal and change directory to the program path
    cd /<path>/p2-ddang.csu

2. To run the binder program:
    python binder.py <prog1> <prog2>...

    Example of combine three binary together into a single file called bound
    python binder.py /bin/ls /bin/date /bin/ps

###############################################################################
# Assignment Analysis
###############################################################################
This assignment helps to provide hand on understanding of how binder work.



###############################################################################
# Credit/Source
###############################################################################
While working on this assignment I used some information/howto from various
sources to help with the code in the assignment.

- samples code provided with the assignment
- virustotal.com website for testing virus detection for part 1
- www.eicar.org website for the sample malware test file
