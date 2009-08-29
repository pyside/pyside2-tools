
add_test(RccTest ${CMAKE_CURRENT_SOURCE_DIR}/run_test.sh
                 ${PYTHON_EXECUTABLE}
                 ${CMAKE_CURRENT_SOURCE_DIR}/rcc_test.py
                 ${CMAKE_CURRENT_SOURCE_DIR}/example.qrc
                 ${CMAKE_CURRENT_SOURCE_DIR} )
