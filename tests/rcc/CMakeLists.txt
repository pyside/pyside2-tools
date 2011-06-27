
add_test(RccTest ${CMAKE_CURRENT_SOURCE_DIR}/run_test.sh
                 ${PYSIDERCC_EXECUTABLE}
                 ${CMAKE_CURRENT_SOURCE_DIR}/rcc_test.py
                 ${CMAKE_CURRENT_SOURCE_DIR}/example.qrc
                 ${CMAKE_CURRENT_SOURCE_DIR} )
add_test(RccImageTest ${CMAKE_CURRENT_SOURCE_DIR}/run_test.sh
                      ${PYSIDERCC_EXECUTABLE}
                      ${CMAKE_CURRENT_SOURCE_DIR}/rcc_image_test.py
                      ${CMAKE_CURRENT_SOURCE_DIR}/image.qrc
                      ${CMAKE_CURRENT_SOURCE_DIR} )

