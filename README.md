# exFat forensic basic info gathering
This is python script I made as was learning basics of exFat filesystem forensics at work. It is my first python script so don't expect enterprise level code but it is a simple code and could be useful for Python learning.

Check Main() function to see programs entry point.

## What it can do?
* Gather and print VBR information;
* Print cluster status based on bitmap position (absolute byte position);
* Carve data out into a file by defining the start and the end clusters.
