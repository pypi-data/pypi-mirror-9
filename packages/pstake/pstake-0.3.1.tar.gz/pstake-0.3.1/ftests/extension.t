Destination file extension name is png::

  $ rm -f other.*
  $ if [ ! -a other.png ]; then echo "Good, no file"; fi
  Good, no file
  $ pstake ${SRCDIR}/example/sample.tex other.png > /dev/null 2>&1
  $ if [ -a other.png ]; then echo "Good, file created"; fi
  Good, file created

Destination file extension name is eps::

  $ rm -f other.*
  $ if [ ! -a other.eps ]; then echo "Good, no file"; fi
  Good, no file
  $ pstake ${SRCDIR}/example/sample.tex other.eps > /dev/null 2>&1
  $ if [ -a other.eps ]; then echo "Good, file created"; fi
  Good, file created

.. vim: set ft=rst:
