# k8-simulation
A basic k8s simulation

## Pre-requisites
- Python 3+
- Python unittest module
- Python matplotlib module

## Getting started
- To run the simulator get into the src directory and run the `runSimulator.py` file with three parameters namely, Kp, Ki and Kd to tune the controllers running the HPAs

## Testing
- Run `./test.sh all` to run the test suite containing all unit test cases
- Run `./test.sh <path_to_unit_test>` to run a particular unit test

## Directories
- test/ contains all the unit test cases
- src/ contains the source code
- tracefiles/ contains the tracefiles for test and actual simulations
- graph/ contains the graphs generated by the various simulations