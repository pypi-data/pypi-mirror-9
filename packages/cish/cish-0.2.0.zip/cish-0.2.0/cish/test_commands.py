# Copyright (c) 2014, Stefan C. Mueller
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
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
import os.path
import shutil
import tempfile

from cish import commands

class TestCommands(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmpdir)

    def test_mkdirs(self):
        """
        Tests the creation of a directory with an existing parent.
        """
        commands.mkdirs(self.get_path("mydir"))
        self.assertTrue(os.path.isdir(self.get_path("mydir")))

    def test_mkdirs_recursively(self):
        """
        Tests the creation of a directory without an existing parent.
        """
        commands.mkdirs(self.get_path("parent/mydir"))
        self.assertTrue(os.path.isdir(self.get_path("parent/mydir")))

    def test_mkdirs_existing(self):
        """
        Tests that existing directories are not changed.
        """
        self.create_files(["mydir/myfile"])
        commands.mkdirs(self.get_path("mydir"))
        self.assertTrue(os.path.isfile(self.get_path("mydir/myfile")))
       
    def test_mkdir_isfile(self):
        """
        Tests that mkdirs fails if the target is an existing file.
        """
        self.create_files(["myfile"])
        self.assertRaises(ValueError, commands.mkdirs, self.get_path("myfile"))

    def test_rm_file(self):
        """
        Test deletion of a file.
        """
        self.create_files(["myfile"])
        commands.rm(self.get_path("myfile"))
        self.assertFalse(os.path.exists(self.get_path("myfile")))

    def test_rm_emptydir(self):
        """
        Test deletion of an empty directory.
        """
        os.mkdir(self.get_path("mydir"))
        commands.rm(self.get_path("mydir"))
        self.assertFalse(os.path.exists(self.get_path("mydir")))

    def test_rm_recursive(self):
        """
        Test deletion of a directory with content.
        """
        self.create_files(["mydir/myfile",
                           "mydir/subdir/anotherfile"])
        commands.rm(self.get_path("mydir"))
        self.assertFalse(os.path.exists(self.get_path("mydir")))

    def test_rm_nonexistant(self):
        """
        Test deletion of a file that does not exist.
        """
        commands.rm(self.get_path("mydir"))
        self.assertFalse(os.path.exists(self.get_path("mydir")))

    def test_pwd(self):
        """
        Tests pwd.
        """
        os.chdir(self.tmpdir)
        self.assertEqual(commands.pwd(), self.tmpdir)

    def test_cd_abs(self):
        """
        Test cd with an absolute path.
        """
        self.create_files(["mydir/myfile",
                           "mydir/subdir/anotherfile"])
        commands.cd(self.get_path("mydir/subdir"))
        self.assertTrue(os.getcwd(), self.get_path("mydir/subdir"))

    def test_cd_relative(self):
        """
        Test cd with a relative path.
        """
        self.create_files(["mydir/myfile",
                           "mydir/subdir/anotherfile"])
        os.chdir(self.get_path("mydir"))
        commands.cd("subdir")
        self.assertTrue(os.getcwd(), self.get_path("mydir/subdir"))

    def test_cd_with(self):
        """
        Test that the path is reset after the `with` statement.
        """
        self.create_files(["mydir/myfile",
                           "mydir/subdir/anotherfile"])
        os.chdir(self.get_path("mydir"))
 
        with commands.cd("subdir") as path:
            self.assertTrue(os.getcwd(), self.get_path("mydir/subdir"))
            self.assertTrue(path, self.get_path("mydir/subdir")) 
        self.assertTrue(os.getcwd(), self.get_path("mydir"))

    def test_cd_with_recursive(self):
        """
        Test that the path is reset after nested `with` statements.
        """
        self.create_files(["mydir/myfile",
                           "mydir/subdir/anotherfile",
                           "mydir/subdir/subsubdir/afile"])
        os.chdir(self.get_path("mydir"))

        with commands.cd("subdir"):
            with commands.cd("subsubdir"): 
                self.assertTrue(os.getcwd(), self.get_path("mydir/subdir/subsubdir"))
            self.assertTrue(os.getcwd(), self.get_path("mydir/subdir"))
        self.assertTrue(os.getcwd(), self.get_path("mydir"))

    def get_path(self, path):
        """
        Returns the absolute path to a file relative to the temporary directory.
        """
        return os.path.join(self.tmpdir, path.replace("/", os.sep))

    def create_files(self, files):
        """
        Takes a list of files (optionally with relative paths)
        and creates them in the temporary directory.
        """
        files = [f.replace("/", os.sep) for f in files]

        for relative_file in files:
            relative_file = relative_file.replace("/", os.sep)
            relative_path, filename = os.path.split(relative_file)
            absolute_path = os.path.join(self.tmpdir, relative_path)
            if not os.path.exists(absolute_path):
                os.makedirs(absolute_path)
            absolute_file = os.path.join(absolute_path, filename)
            with open(absolute_file, 'w') as f:
                f.write(relative_file)

