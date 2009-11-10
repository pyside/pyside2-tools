
set(lupdate_SRC
fetchtr.cpp
main.cpp
merge.cpp
metatranslator.cpp
numberh.cpp
proparser.cpp
sametexth.cpp
simtexth.cpp
translator.cpp
)

set(lupdate_MOC_HEADERS translator.h)
qt4_wrap_cpp(lupdate_MOC_OUTFILES ${lupdate_MOC_HEADERS})

add_executable(pyside-lupdate ${lupdate_SRC} ${lupdate_MOC_OUTFILES})
include_directories(pyside-lupdate
                    ${CMAKE_CURRENT_SOURCE_DIR}
                    ${QT_INCLUDE_DIR}
                    ${QT_QT_INCLUDE_DIR}
                    ${QT_QTXML_INCLUDE_DIR}
                    ${QT_QTCORE_INCLUDE_DIR}
                    ${QT_QTGUI_INCLUDE_DIR})

target_link_libraries(pyside-lupdate
                      ${QT_QTCORE_LIBRARY}
                      ${QT_QTXML_LIBRARY}
                      ${QT_QTGUI_LIBRARY})

install(TARGETS pyside-lupdate RUNTIME DESTINATION bin)
