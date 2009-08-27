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

import sys

from pysideuic.properties import Properties
from qobjectcreator import CompilerCreatorPolicy
import qtproxies

from indenter import createCodeIndenter, getIndenter, write_code

from pysideuic import uiparser


class UICompiler(uiparser.UIParser):
    def __init__(self):
        uiparser.UIParser.__init__(self, qtproxies.QtCore, qtproxies.QtGui,
                CompilerCreatorPolicy())

    def reset(self):
        qtproxies.i18n_strings = []
        uiparser.UIParser.reset(self)

    def setContext(self, context):
        qtproxies.i18n_context = context

    def createToplevelWidget(self, classname, widgetname):
        indenter = getIndenter()
        indenter.level = 0
        indenter.write("from PySide import QtCore, QtGui")
        indenter.write("")
        indenter.write("class Ui_%s(object):" % self.uiname)
        indenter.indent()
        indenter.write("def setupUi(self, %s):" % widgetname)
        indenter.indent()
        w = self.factory.createQObject(classname, widgetname, (),
                                   is_attribute = False,
                                   no_instantiation = True)
        w.baseclass = classname
        w.uiclass = "Ui_%s" % self.uiname
        return w

    def setDelayedProps(self):
        write_code("")
        write_code("self.retranslateUi(%s)" % self.toplevelWidget)
        uiparser.UIParser.setDelayedProps(self)

    def finalize(self):
        indenter = getIndenter()
        indenter.level = 1
        indenter.write("")
        indenter.write("def retranslateUi(self, %s):" % self.toplevelWidget)
        indenter.indent()

        if qtproxies.i18n_strings:
            for s in qtproxies.i18n_strings:
                indenter.write(s)
        else:
            indenter.write("pass")

        indenter.dedent()
        indenter.dedent()

        # Make a copy of the resource modules to import because the parser will
        # reset() before returning.
        self._resources = self.resources

    def compileUi(self, input_stream, output_stream):
        createCodeIndenter(output_stream)
        w = self.parse(input_stream)

        indenter = getIndenter()
        indenter.write("")

        self.factory._cpolicy._writeOutImports()

        for res in self._resources:
            indenter.write("import %s" % res)

        return {"widgetname": str(w),
                "uiclass" : w.uiclass,
                "baseclass" : w.baseclass}
