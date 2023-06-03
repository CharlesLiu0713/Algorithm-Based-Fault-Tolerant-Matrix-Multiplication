##     Algorithm-Based Fault Tolerant Matrix Multiplication

Algorithm Based Fault Tolerance implementation for serial and distributed matrix multiplication.

### Dependencies

This project was implemented using built in Python Libraries, as well as Numpy and Mininet. 

The serial version is completely Python 3.6 compatible and can be run without any further modification.

To enable network communications, the socketserver library was used for TCP data transmission. Due to limitations with the current distribution of the Mininet VM, it may be necessary to roll back to Python 2.7 when using Mininet. This will require using :

`import SocketServer as socketserver`

### Execution

#### Serial

To execute the serial implementation of this code, invoke the "single_driver.py" script from the src directory

This can be done using two files as input, or with no arguments:

`python Serial.py`

If invoked with file names, the script will read in the supplied files and operate on them. If not, the script will automatically generate two 1024 x 1024 random matrices, save them to the current directory, then execute on them. 

CSV input files are expected to be ', ' delimited with newlines to row breaks. See 'csv_io.py' for details.

Output for timing and error insertion, detection, and correction will be written to stdout.

#### Distributed

The distributed version is expected to be run from within the Mininet virtual machine with root access. To run the entire system and automatically create the Mininet network topology, the user will need to invoke the 'run_distributed.py' script with root access. 

First, create a directory for timing and error output logging:

`mkdir output`

Finally, invoke the run script with root access:

`sudo python Distributed.py [<input_csv_1> <input_csv_2>]`

This will launch Mininet, build the topology, run some ping tests, then initiate calculation. No output will be seen other than a completion message, so be patient while the program execute. All output from the central client process and the workers will be logged to files in the 'output' directory. Check the client file first to see if the matrix norm is non-zero, if so, check other files to see where errors occurred.

This will output two files. The results of only the multiplication, stripped of any ABFT checking will be written to 'output.csv'. A result matrix with ABFT checks will be written to 'output_abft.csv'.

Communication is built on an assumed table of IP addresses for the worker processors. If there are issues with connections, verify that the IP's listed in 'multi_driver.py' in the 'processor_addresses' list are valid for the emulated network.
