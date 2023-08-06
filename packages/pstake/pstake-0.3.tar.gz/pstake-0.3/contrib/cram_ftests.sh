#!/bin/bash

# Parse command-line options.
curdir= srcdir=`pwd`
while getopts cs: opt; do
  case $opt in
  c)
    curdir=true
    ;;
  s)
    srcdir="$(cd "$OPTARG" && pwd)"
    ;;
  esac
done
shift $((OPTIND - 1))

# If we want to use the source files for tests.
if [ $curdir ]; then
  export PATH=$srcdir:$PATH
  echo "Prepend $srcdir to \$PATH"
fi

# Back up the old functional-test errors.
mkdir -p tmp/last_ftests_err/
if test -n "$(find . -maxdepth 1 -name 'ftests/*.err' -print -quit)"
then
  mv -f ftests/*.err tmp/last_ftests_err/
fi

# Perform functional tests.
export SRCDIR=${srcdir}
cram --shell=/bin/bash -v $*
