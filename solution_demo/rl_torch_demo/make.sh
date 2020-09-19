#!/bin/bash
mkdir build
cd build
cmake -DCMAKE_PREFIX_PATH=/home/aitrans-server/demo/libtorch .. 
cmake --build . --config Release
make
cd ..