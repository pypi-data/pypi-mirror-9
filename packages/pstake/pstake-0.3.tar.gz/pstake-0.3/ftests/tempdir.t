Simple test the ``-k`` option for keeping temporary directory working, but
validate nothing::

  $ pstake ${SRCDIR}/example/sample.tex -k > /dev/null 2>&1

If we specify a temporary directory with ``--tempdir``, the ``-k`` option
should also be used to prevent the temporary directory gets deleted::

  $ rm -rf tempdir/
  $ if [ ! -a tempdir ]; then echo "Good, no directory"; fi
  Good, no directory
  $ mkdir -p tempdir/
  $ pstake ${SRCDIR}/example/sample.tex --tempdir mytmp/ -k > /dev/null 2>&1
  $ if [ -a tempdir ]; then echo "Good, we still have the directory"; fi
  Good, we still have the directory

.. vim: set ft=rst:
