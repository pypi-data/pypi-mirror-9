#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2014, Yung-Yu Chen <yyc@solvcon.net>
#
# All rights reserved.
#
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the pstake nor the names of its contributors may be
#   used to endorse or promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import unittest
import os
import tempfile
import shutil

import pstake


class TestInitialization(unittest.TestCase):

    def test_ftype(self):
        self.assertEqual(
            repr(pstake.Filename(source='dir1/main.tex',
                                 dest='dir2/', ftype='png')),
            "Filename(source='dir1/main.tex', dest='dir2/main.png')")

    def test_destext(self):
        self.assertEqual(
            repr(pstake.Filename(source='dir1/main.tex',
                                 dest='dir2/other.png')),
            "Filename(source='dir1/main.tex', dest='dir2/other.png')")

    def test_tempdir(self):
        with pstake._remember_cwd():
            try:
                testdir = tempfile.mkdtemp()
                os.chdir(testdir)
                # Use an existing directory.
                os.mkdir('custom_tempdir')
                fn = pstake.Filename(source='dir1/main.tex',
                                     dest='other.png',
                                     tempdir='custom_tempdir')
                self.assertEqual('custom_tempdir', fn.tempdir)
                # If the specified directory doesn't exist, a new one gets
                # created.
                fn = pstake.Filename(source='dir1/main.tex',
                                     dest='other.png',
                                     tempdir='custom_not_there')
                self.assertNotEqual('custom_not_there', fn.tempdir)
                # Housekeeping.
                shutil.rmtree(fn.tempdir)
            finally:
                shutil.rmtree(testdir)

    def test_no_dest(self):
        self.assertEqual(
            repr(pstake.Filename(source='dir1/main.tex', dest='', ftype='png')),
            "Filename(source='dir1/main.tex', dest='main.png')")

    def test_no_destext(self):
        with self.assertRaises(ValueError) as cm:
            pstake.Filename(source='dir1/main.tex', dest='other')
        self.assertEqual(cm.exception.args[0],
                         "can't determine the destination file type")

    def test_both_ftype_destext(self):
        self.assertEqual(
            repr(pstake.Filename(source='dir1/main.tex',
                                 dest='dir2/other.png', ftype='eps')),
            "Filename(source='dir1/main.tex', dest='dir2/other.png')")
        self.assertEqual(
            repr(pstake.Filename(source='dir1/main.tex',
                                 dest='dir2/other', ftype='eps')),
            "Filename(source='dir1/main.tex', dest='dir2/other.eps')")

    def test_missing_ftype_desext(self):
        with self.assertRaises(ValueError) as cm:
            pstake.Filename(source='dir1/main.tex', dest='dir2/')
        self.assertEqual(cm.exception.args[0],
                         "either dest or ftype needs to be specified")

    def test_noslash_nonexisting(self):
        with pstake._remember_cwd():
            try:
                tempdir = tempfile.mkdtemp()
                os.chdir(tempdir)
                # "dir2" is treated as a main file name.
                self.assertEqual(
                    "Filename(source='dir1/main.tex', dest='dir2.png')",
                    repr(pstake.Filename(source='dir1/main.tex',
                                         dest='dir2', ftype='png')))
            finally:
                shutil.rmtree(tempdir)

    def test_noslash_directory(self):
        with pstake._remember_cwd():
            try:
                tempdir = tempfile.mkdtemp()
                os.chdir(tempdir)
                os.mkdir('dir2')
                # "dir2" is a directory and treated as one.
                self.assertEqual(
                    "Filename(source='dir1/main.tex', dest='dir2/main.png')",
                    repr(pstake.Filename(source='dir1/main.tex',
                                         dest='dir2', ftype='png')))
            finally:
                shutil.rmtree(tempdir)


class TestNames(unittest.TestCase):

    def test_source(self):
        fn = pstake.Filename(source='dir1/name.tex',
                             dest='dir2/', ftype='png')
        self.assertEqual(fn.source, 'name.tex')
        self.assertEqual(fn.source, fn.sourcebase)

    def test_dest(self):
        self.assertEqual(
            pstake.Filename(source='dir1/name.tex',
                            dest='dir2/', ftype='png').dest,
            'name.png')
        self.assertEqual(
            pstake.Filename(source='dir1/name.tex',
                            dest='dir2/', ftype='eps').dest,
            'name.eps')

    def test_sourcepath(self):
        cwd = os.getcwd() 
        self.assertEqual(
            pstake.Filename(source='dir1/name.tex',
                            dest='dir2/', ftype='png').sourcepath,
            os.path.join(cwd, 'dir1/name.tex'))

    def test_destpath(self):
        cwd = os.getcwd() 
        self.assertEqual(
            pstake.Filename(source='dir1/name.tex',
                            dest='dir2/', ftype='png').destpath,
            os.path.join(cwd, 'dir2/name.png'))

    def test_destext_lower(self):
        # :py:class:`Filename.destext is always lower case.
        self.assertEqual(pstake.Filename(source='dir1/main.tex',
                                         dest='dir2/other.PNG').destext, 'png')
        self.assertEqual(pstake.Filename(source='dir1/main.tex',
                                         dest='dir2/other.PnG').destext, 'png')

    def test_ftype(self):
        self.assertEqual(
            pstake.Filename(source='dir1/name.tex',
                            dest='dir2/', ftype='png').ftype,
            'png')
        self.assertEqual(
            pstake.Filename(source='dir1/name.tex',
                            dest='dir2/other.png').ftype,
            'png')
        # :py:attr:`Filename.ftype` always equals to
        # :py:attr:`Filename.destext`.
        fn = pstake.Filename(source='dir1/name.tex', dest='dir2/other.png')
        self.assertEqual(fn.ftype, fn.destext)

    def test_intereps(self):
        self.assertEqual(
            pstake.Filename(source='dir1/name.tex',
                            dest='dir2/', ftype='png').intereps,
            'name.eps')
