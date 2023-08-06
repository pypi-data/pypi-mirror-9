Show help::

  $ pstake -h
  usage: pstake [-h] [-V] [--font {None,cmbright}] [-k] [-t DSTEXT] [-q]
                [--cmdout CMDOUT] [--tempdir TEMPDIR]
                src [dst]
  
  Convert a pstricks LaTeX file (.tex) to an image file.
  
  positional arguments:
    src                   source file name
    dst                   destination file name
  
  optional arguments:
    -h, --help            show this help message and exit
    -V, --version         show program's version number and exit
    --font {None,cmbright}
                          font selection (default = None)
    -k                    keep temporary directory
    -t DSTEXT             destination file type (default = png)
    -q, --quiet           suppress terminal output
    --cmdout CMDOUT       sub-command output file (default = None)
    --tempdir TEMPDIR     DANGEROUS! Be sure to set -k, otherwise the temporary
                          directory you specified will be deleted after the
                          script ends.

.. vim: set ft=rst:
