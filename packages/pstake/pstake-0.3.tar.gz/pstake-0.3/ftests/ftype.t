File type png::

  $ rm -f sample.*
  $ if [ ! -a sample.png ]; then echo "Good, no file"; fi
  Good, no file
  $ pstake ${SRCDIR}/example/sample.tex -t png > /dev/null 2>&1
  $ if [ -a sample.png ]; then echo "Good, file created"; fi
  Good, file created

File type eps::

  $ rm -f sample.*
  $ if [ ! -a sample.eps ]; then echo "Good, no file"; fi
  Good, no file
  $ pstake ${SRCDIR}/example/sample.tex -t eps > /dev/null 2>&1
  $ if [ -a sample.eps ]; then echo "Good, file created"; fi
  Good, file created

Default file type is png::

  $ rm -f sample.*
  $ if [ ! -a sample.png ]; then echo "Good, no file"; fi
  Good, no file
  $ pstake ${SRCDIR}/example/sample.tex > /dev/null 2>&1
  $ if [ -a sample.png ]; then echo "Good, file created"; fi
  Good, file created

.. vim: set ft=rst:
