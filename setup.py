#!/usr/bin/env python
# This file is part of the PySide project.
#
# Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
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

from distutils.core import setup

setup(name='PySideUiC',
      version='0.1',
      author='PySide team',
      author_email='contact@pyside.org',
      url='http://www.pyside.org',
      scripts=['pyside-uic'],
      packages=['pysideuic', 'pysideuic.Compiler', 'pysideuic.elementtree'],
      package_data={'pysideuic' : ['widget-plugins/*']})

