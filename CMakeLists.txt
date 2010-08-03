
cmake_minimum_required(VERSION 2.6)
project(pyside-tools)

find_package(PythonInterp REQUIRED)
find_package(Qt4 4.5.0 REQUIRED)
find_package(PySide 0.4.0 REQUIRED)

enable_testing()

set(pyside_tools_MAJOR_VERSION "0")
set(pyside_tools_MINOR_VERSION "2")
set(pyside_tools_MICRO_VERSION "0")
set(pyside_tools_VERSION "${pyside_tools_MAJOR_VERSION}.${pyside_tools_MINOR_VERSION}.${pyside_tools_MICRO_VERSION}")

configure_file(pyside-uic.in pyside-uic @ONLY)

# UIC stuff
execute_process(
    COMMAND ${PYTHON_EXECUTABLE} -c "from distutils import sysconfig; \\
        print sysconfig.get_python_lib(1,0,prefix='${CMAKE_INSTALL_PREFIX}')"
    OUTPUT_VARIABLE SITE_PACKAGE
    OUTPUT_STRIP_TRAILING_WHITESPACE)
if (NOT SITE_PACKAGE)
    message(FATAL_ERROR "Could not detect Python module installation directory.")
endif()

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/pyside-uic
        DESTINATION bin
        PERMISSIONS
        OWNER_EXECUTE OWNER_WRITE OWNER_READ
        GROUP_EXECUTE GROUP_READ
        WORLD_EXECUTE WORLD_READ)


install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/pysideuic
        DESTINATION ${SITE_PACKAGE})

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake"
               "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
               IMMEDIATE @ONLY)

add_custom_target(uninstall "${CMAKE_COMMAND}"
                  -P "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake")

set(ARCHIVE_NAME ${CMAKE_PROJECT_NAME}-${pyside_tools_VERSION})
add_custom_target(dist
    COMMAND mkdir -p "${CMAKE_BINARY_DIR}/${ARCHIVE_NAME}" &&
            git log > "${CMAKE_BINARY_DIR}/${ARCHIVE_NAME}/ChangeLog" &&
            git archive --prefix=${ARCHIVE_NAME}/ HEAD --format=tar --output="${CMAKE_BINARY_DIR}/${ARCHIVE_NAME}.tar" &&
            tar -C "${CMAKE_BINARY_DIR}" --owner=root --group=root -r "${ARCHIVE_NAME}/ChangeLog" -f "${CMAKE_BINARY_DIR}/${ARCHIVE_NAME}.tar" &&
            bzip2 -f9 "${CMAKE_BINARY_DIR}/${ARCHIVE_NAME}.tar" &&
            echo "Source package created at ${CMAKE_BINARY_DIR}/${ARCHIVE_NAME}.tar.bz2.\n"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_subdirectory(pyrcc)
add_subdirectory(pylupdate)
add_subdirectory(tests)

