#!/bin/bash
VER=`python -c 'import pstake; print pstake.__version__'`
rm -rf build/ dist/
python setup.py sdist
