Test SCons support::

  $ rm -rf ${SRCDIR}/tmp/example/
  $ if [ ! -a ${SRCDIR}/tmp/example/ ]; then echo "Good, no directory"; fi
  Good, no directory
  $ scons -C ${SRCDIR}/scons/ > /dev/null 2>&1
  $ if [ -a ${SRCDIR}/tmp/example/sample.eps ]; then echo "Good, file created"; fi
  Good, file created

.. vim: set ft=rst:
