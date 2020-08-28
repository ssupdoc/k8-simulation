#!/bin/bash

# Run with all to run the complete test suite or mention the unittest to test with

if [ $1 == 'all' ]; then
    python3 -m unittest discover test "*_test.py" --verbose
else
    python3 -m unittest $1 --verbose
fi