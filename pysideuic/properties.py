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

import logging
import operator
import string

from pysideuic.exceptions import UnsupportedPropertyError

from icon_cache import IconCache


logger = logging.getLogger(__name__)
DEBUG = logger.debug

QtCore = None
QtGui = None


# A translation table for converting ASCII lower case to upper case.
_ascii_trans_table = string.maketrans(string.ascii_lowercase, string.ascii_uppercase)

# Convert a string to ASCII upper case irrespective of the current locale.
def ascii_upper(s):
    return s.translate(_ascii_trans_table)


def int_list(prop):
    return [int(child.text) for child in prop]

def float_list(prop):
    return [float(child.text) for child in prop]

bool_ = lambda v: v == "true"

def needsWidget(func):
    func.needsWidget = True
    return func


class Properties(object):
    def __init__(self, factory, QtCore_mod, QtGui_mod):
        global QtGui, QtCore
        QtGui = QtGui_mod
        QtCore = QtCore_mod
        self.factory = factory
        self.reset()

    def reset(self):
        self.buddies = []
        self.delayed_props = []
        self.icon_cache = IconCache(self.factory, QtGui)

    def _pyEnumMember(self, cpp_name):
        try:
            prefix, membername = cpp_name.split("::")
            DEBUG(membername)
            if prefix == "Qt":
                return getattr(QtCore.Qt, membername)
            else:
                return getattr(getattr(QtGui, prefix), membername)
        except ValueError:
            return getattr(getattr(QtGui, self.wclass), cpp_name)

    def _set(self, prop):
        return reduce(operator.or_, [self._pyEnumMember(value)
                                     for value in prop.text.split('|')])

    def _enum(self, prop):
        return self._pyEnumMember(prop.text)

    def _number(self, prop):
        return int(prop.text)

    _uInt = _longLong = _uLongLong = _number

    def _double(self, prop):
        return float(prop.text)

    def _bool(self, prop):
        return prop.text == 'true'

    def _stringlist(self, prop):
        return [self._string(p) for p in prop]

    def _string(self, prop):
        if prop.get("notr", None) == "true":
            return self._cstring(prop)

        if prop.text is None:
            return ""

        text = prop.text.encode("UTF-8")
        return QtGui.QApplication.translate(self.uiname, text, None,
                QtGui.QApplication.UnicodeUTF8)

    _char = _string

    def _cstring(self, prop):
        return str(prop.text)

    def _color(self, prop):
        args = int_list(prop)

        # Handle the optional alpha component.
        alpha = int(prop.get("alpha", "255"))

        if alpha != 255:
            args.append(alpha)

        return QtGui.QColor(*args)

    def _point(self, prop):
        return QtCore.QPoint(*int_list(prop))

    def _pointf(self, prop):
        return QtCore.QPointF(*float_list(prop))

    def _rect(self, prop):
        return QtCore.QRect(*int_list(prop))

    def _rectf(self, prop):
        return QtCore.QRectF(*float_list(prop))

    def _size(self, prop):
        return QtCore.QSize(*int_list(prop))

    def _sizef(self, prop):
        return QtCore.QSizeF(*float_list(prop))

    def _pixmap(self, prop):
        return QtGui.QPixmap(prop.text.replace("\\", "\\\\"))

    def _iconset(self, prop):
        return self.icon_cache.get_icon(prop)

    def _url(self, prop):
        return QtCore.QUrl(prop[0].text)

    def _cursor(self, prop):
        return QtGui.QCursor(QtCore.Qt.CursorShape(int(prop.text)))

    def _date(self, prop):
        return QtCore.QDate(*int_list(prop))

    def _datetime(self, prop):
        args = int_list(prop)
        return QtCore.QDateTime(QtCore.QDate(*args[-3:]), QtCore.QTime(*args[:-3]))

    def _time(self, prop):
        return QtCore.QTime(*int_list(prop))

    def _palette(self, prop):
        palette = self.factory.createQObject("QPalette", "palette", (),
                                                   is_attribute=False)
        for palette_elem in prop:
            sub_palette = getattr(QtGui.QPalette, palette_elem.tag.title())
            for role, color in enumerate(palette_elem):
                if color.tag == 'color':
                    # Handle simple colour descriptions where the role is
                    # implied by the colour's position.
                    palette.setColor(sub_palette,
                            QtGui.QPalette.ColorRole(role), self._color(color))
                elif color.tag == 'colorrole':
                    role = getattr(QtGui.QPalette, color.get('role'))
                    brushstyle = getattr(QtCore.Qt, color[0].get('brushstyle'))
                    color = color[0][0]

                    brush = self.factory.createQObject("QBrush", "brush",
                                                    (self._color(color), ),
                                                    is_attribute=False)
                    brush.setStyle(brushstyle)
                    palette.setBrush(sub_palette, role, brush)
                else:
                    raise UnsupportedPropertyError, color.tag

        return palette

    #@needsWidget
    def _sizepolicy(self, prop, widget):
        values = [int(child.text) for child in prop]

        if len(values) == 2:
            # Qt v4.3.0 and later.
            horstretch, verstretch = values
            hsizetype = getattr(QtGui.QSizePolicy, prop.get('hsizetype'))
            vsizetype = getattr(QtGui.QSizePolicy, prop.get('vsizetype'))
        else:
            hsizetype, vsizetype, horstretch, verstretch = values
            hsizetype = QtGui.QSizePolicy.Policy(hsizetype)
            vsizetype = QtGui.QSizePolicy.Policy(vsizetype)

        sizePolicy = self.factory.createQObject("QSizePolicy", "sizePolicy",
                (hsizetype, vsizetype), is_attribute=False)
        sizePolicy.setHorizontalStretch(horstretch)
        sizePolicy.setVerticalStretch(verstretch)
        sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        return sizePolicy
    _sizepolicy = needsWidget(_sizepolicy)

    # font needs special handling/conversion of all child elements.
    _font_attributes = (("Family",    str),
                        ("PointSize", int),
                        ("Weight",    int),
                        ("Italic",    bool_),
                        ("Underline", bool_),
                        ("StrikeOut", bool_),
                        ("Bold",      bool_))

    def _font(self, prop):
        newfont = self.factory.createQObject("QFont", "font", (),
                                                     is_attribute = False)
        for attr, converter in self._font_attributes:
            v = prop.findtext("./%s" % (attr.lower(),))
            if v is None:
                continue

            getattr(newfont, "set%s" % (attr,))(converter(v))
        return newfont

    def _cursorShape(self, prop):
        return getattr(QtCore.Qt, prop.text)

    def convert(self, prop, widget = None):
        try:
            func = getattr(self, "_" + prop[0].tag)
        except AttributeError:
            raise UnsupportedPropertyError, prop[0].tag
        else:
            args = {}
            if getattr(func, "needsWidget", False):
                assert widget is not None
                args["widget"] = widget

            return func(prop[0], **args)


    def _getChild(self, elem_tag, elem, name, default = None):
        for prop in elem.findall(elem_tag):
            if prop.attrib["name"] == name:
                if prop[0].tag == "enum":
                    return prop[0].text
                else:
                    return self.convert(prop)
        else:
            return default

    def getProperty(self, elem, name, default = None):
        return self._getChild("property", elem, name, default)

    def getAttribute(self, elem, name, default = None):
        return self._getChild("attribute", elem, name, default)

    def setProperties(self, widget, elem):
        try:
            self.wclass = elem.attrib["class"]
        except KeyError:
            pass
        for prop in elem.findall("property"):
            if prop[0].text is None:
                continue
            propname = prop.attrib["name"]
            DEBUG("setting property %s" % (propname,))

            try:
                stdset = bool(int(prop.attrib["stdset"]))
            except KeyError:
                stdset = True

            if not stdset:
                self._setViaSetProperty(widget, prop)
            elif hasattr(self, propname):
                getattr(self, propname)(widget, prop)
            else:
                getattr(widget, "set%s%s" % (ascii_upper(propname[0]),
                        propname[1:]))(self.convert(prop, widget))

    # SPECIAL PROPERTIES
    # If a property has a well-known value type but needs special,
    # context-dependent handling, the default behaviour can be overridden here.

    # Delayed properties will be set after the whole widget tree has been
    # populated.
    def _delay(self, widget, prop):
        propname = prop.attrib["name"]
        self.delayed_props.append((getattr(widget,
                "set%s%s" % (ascii_upper(propname[0]), propname[1:])),
                self.convert(prop)))

    # These properties will be set with a widget.setProperty call rather than
    # calling the set<property> function.
    def _setViaSetProperty(self, widget, prop):
        widget.setProperty(prop.attrib["name"], self.convert(prop))

    # Ignore the property.
    def _ignore(self, widget, prop):
        pass

    # Define properties that use the canned handlers.
    currentIndex = _delay
    currentRow = _delay

    showDropIndicator = _setViaSetProperty
    intValue = _setViaSetProperty
    value = _setViaSetProperty

    objectName = _ignore
    leftMargin = _ignore
    topMargin = _ignore
    rightMargin = _ignore
    bottomMargin = _ignore
    horizontalSpacing = _ignore
    verticalSpacing = _ignore

    # buddy setting has to be done after the whole widget tree has been
    # populated.  We can't use delay here because we cannot get the actual
    # buddy yet.
    def buddy(self, widget, prop):
        self.buddies.append((widget, prop[0].text))

    # geometry is handled specially if set on the toplevel widget.
    def geometry(self, widget, prop):
        if widget.objectName() == self.uiname:
            geom = int_list(prop[0])
            widget.resize(geom[2], geom[3])
        else:
            widget.setGeometry(self._rect(prop[0]))

    def orientation(self, widget, prop):
        # If the class is a QFrame, it's a line.
        if widget.metaObject().className() == "QFrame":
            widget.setFrameShape(
                {"Qt::Horizontal": QtGui.QFrame.HLine,
                 "Qt::Vertical"  : QtGui.QFrame.VLine}[prop[0].text])

            # In Qt Designer, lines appear to be sunken, QFormBuilder loads
            # them as such, uic generates plain lines.  We stick to the look in
            # Qt Designer.
            widget.setFrameShadow(QtGui.QFrame.Sunken)
        else:
            widget.setOrientation(self._enum(prop[0]))

    # The isWrapping attribute of QListView is named inconsistently, it should
    # be wrapping.
    def isWrapping(self, widget, prop):
        widget.setWrapping(self.convert(prop))

    # This is a pseudo-property injected to deal with setContentsMargin()
    # introduced in Qt v4.3.
    def pyuicContentsMargins(self, widget, prop):
        widget.setContentsMargins(*int_list(prop))

    # This is a pseudo-property injected to deal with setHorizontalSpacing()
    # and setVerticalSpacing() introduced in Qt v4.3.
    def pyuicSpacing(self, widget, prop):
        horiz, vert = int_list(prop)

        if horiz == vert:
            widget.setSpacing(horiz)
        else:
            if horiz >= 0:
                widget.setHorizontalSpacing(horiz)

            if vert >= 0:
                widget.setVerticalSpacing(vert)
