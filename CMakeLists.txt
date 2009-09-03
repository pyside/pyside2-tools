
cmake_minimum_required(VERSION 2.6)
project(PYSIDE-TOOLS)

find_package(PythonInterp REQUIRED)
find_package(Qt4 4.5.0 REQUIRED)

enable_testing()

add_subdirectory(pyrcc)
add_subdirectory(tests)


# UIC stuff
execute_process(
    COMMAND ${PYTHON_EXECUTABLE} -c "from distutils import sysconfig; \\
        print sysconfig.get_python_lib(1,0,prefix='${CMAKE_INSTALL_PREFIX}')"
    OUTPUT_VARIABLE SITE_PACKAGE
    OUTPUT_STRIP_TRAILING_WHITESPACE)
if (NOT SITE_PACKAGE)
    message(FATAL_ERROR "Could not detect Python module installation directory.")
endif (NOT SITE_PACKAGE)

install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/pyside-uic
        DESTINATION bin)

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/pysideuic
        DESTINATION ${SITE_PACKAGE})

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake"
               "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
               IMMEDIATE @ONLY)

add_custom_target(uninstall "${CMAKE_COMMAND}"
                  -P "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake")
