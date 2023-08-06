#!/bin/bash

# Initialize return value.
retval=0
version=`python -c "import pstake; print pstake.__version__"`
pkgname=pstake-${version}

# Define utility function.
run_cmd () {
  echo $1 
  $1
  lret=$?; if [[ $lret != 0 ]]; then retval=$lret; fi
}  

# Install dependency.
run_cmd "sudo apt-get update"
run_cmd "sudo apt-get install texlive-base texlive-generic-extra texlive-latex-extra texlive-math-extra texlive-pstricks imagemagick"
pip install -r requirements.txt --use-mirrors

# Test with the source code.
cd ${WORKSPACE}/
run_cmd "nosetests -v"

# Run the release script to package.
run_cmd "contrib/release.sh"

# Install from the package.
run_cmd "mkdir -p ${WORKSPACE}/tmp/"
cd ${WORKSPACE}/tmp/
run_cmd "tar xfz ../dist/${pkgname}.tar.gz"
cd ${pkgname}
run_cmd "python setup.py install"

# Test with the installed code.
cd ${WORKSPACE}/tmp/
run_cmd '../contrib/cram_ftests.sh -s ../ ../ftests/*.t'

# Return with the real exit code.
exit $retval
