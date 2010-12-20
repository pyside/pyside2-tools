# This file is part of the PySide project.
#
# Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
# Copyright (C) 2009 Riverbank Computing Limited.
# Copyright (C) 2009 Torsten Marek
#
# Contact: PySide team <pyside@openbossa.org>
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

import re
import sys

from indenter import write_code


i18n_strings = []
i18n_context = ""

def i18n_print(string):
    i18n_strings.append(string)

def moduleMember(module, name):
    if module == "":
        return name
    else:
        return "%s.%s" % (module, name)

def obj_to_argument(obj):
    if isinstance(obj, str):
        arg = obj.replace('"', '\\"')

        if '\n' in arg:
            arg = '"""%s"""' % arg
        else:
            arg = '"%s"' % arg
    else:
        arg = str(obj)

    return arg

def i18n_void_func(name):
    def _printer(self, *args):
        i18n_print("%s.%s(%s)" % (self, name, ", ".join(map(obj_to_argument, args))))
    return _printer

def i18n_func(name):
    def _printer(self, rname, *args):
        i18n_print("%s = %s.%s(%s)" % (rname, self, name, ", ".join(map(obj_to_argument, args))))
        return Literal(rname)

    return _printer

def strict_getattr(module, clsname):
    cls = getattr(module, clsname)
    if issubclass(cls, LiteralProxyClass):
        raise AttributeError, cls
    else:
        return cls

class Literal(object):
    """Literal(string) -> new literal

    string will not be quoted when put into an argument list"""
    def __init__(self, string):
        self.string = string

    def __str__(self):
        return self.string

    def __or__(self, r_op):
        return Literal("%s|%s" % (self, r_op))

class i18n_string(object):
    """i18n_string(string)

    string will be UTF-8-encoded, escaped, quoted and translated when included
    into a function call argument list."""
    _esc_regex = re.compile(r"(\"|\'|\\)")
    def __init__(self, string):
        self.string = string

    def escape(self, text):
        x = self._esc_regex.sub(r"\\\1", text)
        return re.sub(r"\n", r'\\n"\n"', x)

    def __str__(self):
        return "QtGui.QApplication.translate(\"%s\", \"%s\", None, QtGui.QApplication.UnicodeUTF8)" % (i18n_context, self.escape(self.string))


# Classes with this flag will be handled as literal values. If functions are
# called on these classes, the literal value changes.
# Example:
# the code
# >>> QSize(9,10).expandedTo(...)
# will print just that code.
AS_ARGUMENT = 2

# ATTENTION: currently, classes can either be literal or normal. If a class
# should need both kinds of behaviour, the code has to be changed.

class ProxyClassMember(object):
    def __init__(self, proxy, function_name, flags):
        self.proxy = proxy
        self.function_name = function_name
        self.flags = flags

    def __str__(self):
        return "%s.%s" % (self.proxy, self.function_name)

    def __call__(self, *args):
        func_call = "%s.%s(%s)" % (self.proxy,
                                   self.function_name,
                                   ", ".join(map(obj_to_argument, args)))
        if self.flags & AS_ARGUMENT:
            self.proxy._uic_name = func_call
            return self.proxy
        else:
            needs_translation = False
            for arg in args:
                if isinstance(arg, i18n_string):
                    needs_translation = True
            if needs_translation:
                i18n_print(func_call)
            else:
                write_code(func_call)


class ProxyType(type):
    def __init__(*args):
        type.__init__(*args)
        for cls in args[0].__dict__.itervalues():
            if type(cls) is ProxyType:
                cls.module = args[0].__name__

        if not hasattr(args[0], "module"):
            args[0].module = ""

    def __getattribute__(cls, name):
        try:
            return type.__getattribute__(cls, name)
        except AttributeError:
            return type(name, (LiteralProxyClass,),
                        {"module": moduleMember(type.__getattribute__(cls, "module"),
                                                type.__getattribute__(cls, "__name__"))})

    def __str__(cls):
        return moduleMember(type.__getattribute__(cls, "module"),
                            type.__getattribute__(cls, "__name__"))

    def __or__(self, r_op):
        return Literal("%s|%s" % (self, r_op))


class ProxyClass(object):
    __metaclass__ = ProxyType
    flags = 0

    def __init__(self, objectname, is_attribute, args=(), noInstantiation=False):
        if objectname:
            if is_attribute:
                objectname = "self." + objectname

            self._uic_name = objectname
        else:
            self._uic_name = "Unnamed"

        if not noInstantiation:
            funcall = "%s(%s)" % \
                    (moduleMember(self.module, self.__class__.__name__),
                    ", ".join(map(str, args)))

            if objectname:
                funcall = "%s = %s" % (objectname, funcall)

            write_code(funcall)

    def __str__(self):
        return self._uic_name

    def __getattribute__(self, attribute):
        try:
            return object.__getattribute__(self, attribute)
        except AttributeError:
            return ProxyClassMember(self, attribute, self.flags)


class LiteralProxyClass(ProxyClass):
    """LiteralObject(*args) -> new literal class

    a literal class can be used as argument in a function call

    >>> class Foo(LiteralProxyClass): pass
    >>> str(Foo(1,2,3)) == "Foo(1,2,3)"
    """
    flags = AS_ARGUMENT
    def __init__(self, *args):
        self._uic_name = "%s(%s)" % \
                     (moduleMember(self.module, self.__class__.__name__),
                      ", ".join(map(obj_to_argument, args)))


class ProxyNamespace(object):
    __metaclass__ = ProxyType


# These are all the Qt classes used by pyuic4 in their namespaces. If a class
# is missing, the compiler will fail, normally with an AttributeError.
#
# For adding new classes:
#     - utility classes used as literal values do not need to be listed
#       because they are created on the fly as subclasses of LiteralProxyClass
#     - classes which are *not* QWidgets inherit from ProxyClass and they
#       have to be listed explicitly in the correct namespace. These classes
#       are created via a ProxyQObjectCreator
#     - new QWidget-derived classes have to inherit from qtproxies.QWidget
#       If the widget does not need any special methods, it can be listed
#       in _qwidgets

class QtCore(ProxyNamespace):
    class Qt(ProxyNamespace):
        pass

    ## connectSlotsByName and connect have to be handled as class methods,
    ## otherwise they would be created as LiteralProxyClasses and never be
    ## printed
    class QMetaObject(ProxyClass):
        def connectSlotsByName(cls, *args):
            ProxyClassMember(cls, "connectSlotsByName", 0)(*args)
        connectSlotsByName = classmethod(connectSlotsByName)


    class QObject(ProxyClass):
        def metaObject(self):
            class _FakeMetaObject(object):
                def className(*args):
                    return self.__class__.__name__
            return _FakeMetaObject()

        def objectName(self):
            return self._uic_name.split(".")[-1]

        def connect(cls, *args):
            ProxyClassMember(cls, "connect", 0)(*args)
        connect = classmethod(connect)

_qwidgets = (
    "QAbstractItemView",
    "QCalendarWidget", "QCheckBox", "QColumnView", "QCommandLinkButton",
    "QDateEdit", "QDateTimeEdit", "QDial", "QDialog", "QDialogButtonBox",
    "QDockWidget", "QDoubleSpinBox",
    "QFrame",
    "QGraphicsView", "QGroupBox",
    "QLabel", "QLCDNumber", "QLineEdit", "QListView",
    "QMainWindow", "QMdiArea", "QMenuBar",
    "QPlainTextEdit", "QProgressBar", "QPushButton",
    "QRadioButton",
    "QScrollArea", "QScrollBar", "QSlider", "QSpinBox", "QSplitter",
    "QStackedWidget", "QStatusBar",
    "QTableView", "QTextBrowser", "QTextEdit", "QTimeEdit", "QToolBar",
    "QToolButton", "QTreeView", "QWizard", "QWizardPage")

class QtGui(ProxyNamespace):
    class QApplication(QtCore.QObject):
        def translate(uiname, text, context, encoding):
            return i18n_string(text or "")
        translate = staticmethod(translate)

    class QIcon(ProxyClass): pass
    class QBrush(ProxyClass): pass
    class QPalette(ProxyClass): pass
    class QFont(ProxyClass): pass
    class QSpacerItem(ProxyClass): pass
    class QSizePolicy(ProxyClass): pass
    ## QActions inherit from QObject for the metaobject stuff
    ## and the hierarchy has to be correct since we have a
    ## isinstance(x, QtGui.QLayout) call in the ui parser
    class QAction(QtCore.QObject): pass
    class QActionGroup(QtCore.QObject): pass
    class QLayout(QtCore.QObject): pass
    class QGridLayout(QLayout): pass
    class QHBoxLayout(QLayout): pass
    class QVBoxLayout(QLayout): pass
    class QFormLayout(QLayout): pass

    class QWidget(QtCore.QObject):
        def font(self):
            return Literal("%s.font()" % self)

        def minimumSizeHint(self):
            return Literal("%s.minimumSizeHint()" % self)

        def sizePolicy(self):
            sp = LiteralProxyClass()
            sp._uic_name = "%s.sizePolicy()" % self
            return sp

    class QListWidgetItem(ProxyClass): pass

    class QListWidget(QWidget):
        isSortingEnabled = i18n_func("isSortingEnabled")
        setSortingEnabled = i18n_void_func("setSortingEnabled")

        def item(self, row):
            return QtGui.QListWidgetItem("%s.item(%i)" % (self, row), False,
                    (), noInstantiation=True)

    class QTreeWidgetItem(ProxyClass):
        def child(self, index):
            return QtGui.QTreeWidgetItem("%s.child(%i)" % (self, index),
                    False, (), noInstantiation=True)

    class QTreeWidget(QWidget):
        isSortingEnabled = i18n_func("isSortingEnabled")
        setSortingEnabled = i18n_void_func("setSortingEnabled")

        def headerItem(self):
            return QtGui.QWidget("%s.headerItem()" % self, False, (),
                    noInstantiation=True)

        def topLevelItem(self, index):
            return QtGui.QTreeWidgetItem("%s.topLevelItem(%i)" % (self, index),
                    False, (), noInstantiation=True)

    class QTableWidgetItem(ProxyClass): pass

    class QTableWidget(QWidget):
        isSortingEnabled = i18n_func("isSortingEnabled")
        setSortingEnabled = i18n_void_func("setSortingEnabled")

        def item(self, row, col):
            return QtGui.QTableWidgetItem("%s.item(%i, %i)" % (self, row, col),
                    False, (), noInstantiation=True)

        def horizontalHeaderItem(self, col):
            return QtGui.QTableWidgetItem("%s.horizontalHeaderItem(%i)" % (self, col),
                    False, (), noInstantiation=True)

        def verticalHeaderItem(self, row):
            return QtGui.QTableWidgetItem("%s.verticalHeaderItem(%i)" % (self, row),
                    False, (), noInstantiation=True)

    class QMenu(QWidget):
        def menuAction(self):
            return Literal("%s.menuAction()" % self)

    class QTabWidget(QWidget):
        def addTab(self, *args):
            i18n_print("%s.setTabText(%s.indexOf(%s), %s)" % \
                       (self._uic_name, self._uic_name, args[0], args[-1]))
            pargs = args[:-1] + ("",)
            ProxyClassMember(self, "addTab", 0)(*pargs)

        def indexOf(self, page):
            return Literal("%s.indexOf(%s)" % (self, page))

    class QToolBox(QWidget):
        def addItem(self, *args):
            i18n_print("%s.setItemText(%s.indexOf(%s), %s)" % \
                       (self._uic_name, self._uic_name, args[0], args[-1]))
            pargs = args[:-1] + ("",)
            ProxyClassMember(self, "addItem", 0)(*pargs)

        def indexOf(self, page):
            return Literal("%s.indexOf(%s)" % (self, page))

    class QComboBox(QWidget): pass
    class QFontComboBox(QComboBox): pass
    class QDialog(QWidget): pass
    class QWizard(QDialog): pass

    # Add all remaining classes.
    for _class in _qwidgets:
        if not locals().has_key(_class):
            locals()[_class] = type(_class, (QWidget, ), {})
