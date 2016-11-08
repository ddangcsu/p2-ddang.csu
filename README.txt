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
#  Document Sections
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

- Dr. Gofman for help on C++ codes on fork, supress child stdout, installation
of libssh library on the VM, and also how to compile the program
