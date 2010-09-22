
add_executable(pyside-rcc main.cpp rcc.cpp)
include_directories(pyside-rcc
                    ${QT_INCLUDE_DIR}
                    ${QT_QT_INCLUDE_DIR}
                    ${QT_QTXML_INCLUDE_DIR}
                    ${QT_QTCORE_INCLUDE_DIR})

target_link_libraries(pyside-rcc
                      ${QT_QTCORE_LIBRARY}
                      ${QT_QTXML_LIBRARY})

install(TARGETS pyside-rcc RUNTIME DESTINATION bin)
