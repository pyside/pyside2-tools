
cmake_minimum_required(VERSION 2.6)
project(PYSIDE-TOOLS)

find_package(PythonInterp REQUIRED)
find_package(Qt4 4.5.0 REQUIRED)

enable_testing()

add_subdirectory(pyrcc)
add_subdirectory(tests)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake"
               "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
               IMMEDIATE @ONLY)

add_custom_target(uninstall "${CMAKE_COMMAND}"
                  -P "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake")
