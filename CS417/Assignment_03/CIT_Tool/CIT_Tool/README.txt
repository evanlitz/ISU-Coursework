To use this tool, copy the file to a directory on pyrite.
From a terminal shell move to the directory where the file is and untar it.

> tar -xvf CIT_Tool.tar.gz

This will create a diretory called CIT_Tool

changed  to this directory:

> cd CIT_Tool

To run the program type:

> ./cit_generate input.txt -F

This will create an output file called "cit_sample.out".
Let's look at the input and output files now.
Note - if you don't use the -F flag you will get a file called "cit_sample.xxxxx.out" where x is a large random number.


Format of the input file:
input.txt

Input file format:
t
k
m_1 x_1
m_2 x_2
...
m_p x_p

Where t is the strength (basic usage is t=2 or pairwise). This is combining all pairs of choices for combinations togehter. 
k is the number of factors (parameters+environments in TSL)
m_i,x_i are pairs indicating the model with m=number of values (choices) for a 
parameter and X the number of parameters with this number of values. 
The sum of all x_is should equal k.

Example
2
5
3 4
2 1

This will generate a pairwise test suite. There are parameters
The first 4 have 3 choices and the last one is binary (e.g. on/off)
