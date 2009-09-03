#!/bin/sh

# This is a nasty workaround of a CTest limitation
# of setting the environment variables for the test.

# $1: python executable
# $2: python test
# $3: qrc file

export PYTHONPATH=$PYTHONPATH:`pwd`
pyside-rcc4 -o `basename $3 .qrc`_rc.py $3
cd $4
$1 $2
