# This file is part of the PySide project.
#
# Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
# Copyright (C) 2009 Riverbank Computing Limited.
# Copyright (C) 2009 Torsten Marek
#
# Contact: PySide team <contact@pyside.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA

import exceptions
import time

__all__ = ("compileUi")

from pysideuic.Compiler import indenter, compiler

_header = """# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '%s'
#
# Created: %s
#      by: PySide uic UI code generator
#
# WARNING! All changes made in this file will be lost!

"""

_display_code = """
if __name__ == "__main__":
\timport sys
\tapp = QtGui.QApplication(sys.argv)
\t%(widgetname)s = QtGui.%(baseclass)s()
\tui = %(uiclass)s()
\tui.setupUi(%(widgetname)s)
\t%(widgetname)s.show()
\tsys.exit(app.exec_())
"""

def compileUi(uifile, pyfile, execute=False, indent=4):
    """compileUi(uifile, pyfile, execute=False, indent=4)

    Creates a Python module from a Qt Designer .ui file.

    uifile is a file name or file-like object containing the .ui file.
    pyfile is the file-like object to which the Python code will be written to.
    execute is optionally set to generate extra Python code that allows the
    code to be run as a standalone application.  The default is False.
    indent is the optional indentation width using spaces.  If it is 0 then a
    tab is used.  The default is 4.
    """
    try:
        uifname = uifile.name
    except AttributeError:
        uifname = uifile

    indenter.indentwidth = indent

    pyfile.write(_header % (uifname, time.ctime()))

    winfo = compiler.UICompiler().compileUi(uifile, pyfile)

    if execute:
        indenter.write_code(_display_code % winfo)
