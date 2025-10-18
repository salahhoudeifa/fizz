# fizz
a simple fuzz testing program

fuzzing is the automated process of generating random data -usually unexpected or invalid- and providing it as input to a target program. it helps with discovering bugs and vulnerabilities in a given program.

this project aims to: create a simulation to demonstrate the use of fuzzing in bug detection.

to use fizz, enter the following command:
``` python3 main.py [[type of fuzzing technique you wish to use]] [[target program]] ```

it will then generate a log with all the errors and store it in the current working directory.

if it finds any valid inputs, it'll store them in the "corpus" folder for later use.

fizz employs a few techniques:
-- generation-based: the fuzzer generates the data from scratch and feeds it into the program

-- mutation-based: the fuzzer takes the valid data from the "corpus" folder and introduces small changes to possibly find new behavior. this method is more effective at finding new unexpected behavior.

fizz currently only supports raw code, but it will support API fuzzing and web fuzzing in the future.
