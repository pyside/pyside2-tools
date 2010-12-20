
add_subdirectory(rcc)

add_test("test_qwizard" ${PYTHON_EXECUTABLE} ${CMAKE_BINARY_DIR}/pyside-uic "${CMAKE_CURRENT_SOURCE_DIR}/qwizard_test.ui")
set_tests_properties("test_qwizard" PROPERTIES
                     ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}")
