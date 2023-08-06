Suppressing sub-command output::

  $ rm -f sample.*
  $ if [ ! -a sample.png ]; then echo "Good, no file"; fi
  Good, no file
  $ pstake ${SRCDIR}/example/sample.tex --cmdout /dev/null -t png
  Working in * ... (glob)
  latex sample.tex
  dvips sample.dvi -q -E -o sample.eps
  convert -density 300 -units PixelsPerInch sample.eps */sample.png (glob)
  Removing the temporary working directory * ... Done (glob)
  $ if [ -a sample.png ]; then echo "Good, file created"; fi
  Good, file created

.. vim: set ft=rst:
