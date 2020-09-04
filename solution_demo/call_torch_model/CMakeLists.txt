cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(custom_ops)

set(Torch_DIR /home/aitrans-server/demo/libtorch/share/cmake/Torch)
find_package(Torch REQUIRED)

# generate .so file
SET(LIBRARY_OUTPUT_PATH "./" )
ADD_LIBRARY(solution SHARED solution.cxx ${Torch_DIR}/../../../lib ${CURRENT_INCLUDE})

# if there is main function
# add_executable(solution solution.cxx)

target_link_libraries(solution "${TORCH_LIBRARIES}")
set_property(TARGET solution PROPERTY CXX_STANDARD 14)