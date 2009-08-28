
add_executable(pyside-rcc4 main.cpp rcc.cpp)
include_directories(pyside-rcc4
                    ${QT_INCLUDE_DIR}
                    ${QT_QT_INCLUDE_DIR}
                    ${QT_QTCORE_INCLUDE_DIR})

target_link_libraries(pyside-rcc4
                      ${QT_QTCORE_LIBRARY}
                      ${QT_QTXML_LIBRARY})

install(TARGETS pyside-rcc4 RUNTIME DESTINATION bin)
