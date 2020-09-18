#!/bin/bash
mkdir build
cd build
cmake -DCMAKE_PREFIX_PATH=/home/libtorch .. 
cmake --build . --config Release
make
cd ..