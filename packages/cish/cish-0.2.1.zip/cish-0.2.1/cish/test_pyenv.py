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
import subprocess
import json

from cish import pyenv

class TestPyEnv(unittest.TestCase):
    """
    Unit-tests for :class:`pyenv.PyEnv`.
    """

    def setUp(self):
        self.cwd = os.getcwd()
        self.tmpdir = tempfile.mkdtemp()
    
    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmpdir)

    def test_linux_style(self):
        """
        Python installed using linux distribution packages
        usually ends up in '/usr/bin', as do all the utilities.
        """
        self.create_files(["bin/python",
                           "bin/pip",
                           "bin/virtualenv"])
        env = pyenv.from_interpreter(self.get_path("bin/python"))
        self.assertEqual(env.find_executable("pip"), self.get_path("bin/pip"))
        
    def test_windows_style(self):
        """
        Windows installations have the utilities in a separate directory.
        """
        self.create_files(["python.exe",
                           "Scripts/pip",
                           "Scripts/virtualenv"])
        env = pyenv.from_interpreter(self.get_path("python.exe"))
        self.assertEqual(env.find_executable("pip"), self.get_path("Scripts/pip"))
        
    def test_prefer_wpython(self):
        """
        Windows installations have the utilities in a separate directory.
        """
        self.create_files(["python.exe",
                           "wpython.exe"])
        env = pyenv.from_interpreter(self.get_path("python.exe"))
        self.assertEqual(env.find_executable("python"), self.get_path("wpython.exe"))
        
    def test_w_prefix_only_for_python(self):
        """
        On windows installations the interpreter might have a `w` prefix,
        but this is not used for other executables, so we should not 
        return the wrong one.
        """
        self.create_files(["python.exe",
                           "wpip.exe",
                           "pip.exe"])
        env = pyenv.from_interpreter(self.get_path("python.exe"))
        self.assertEqual(env.find_executable("pip"), self.get_path("pip.exe"))
       
    def test_getattr(self):
        """
        Test if we can invoke the python interpreter using a method on the environment.
        """
        env = pyenv.interpeter_pyenv() 
        env.python("-c", "pass")

    def test_virtualenv_abs(self):
        """
        Tests if we can create a virtual environment giving an absolute path.
        """
        env = pyenv.interpeter_pyenv()
        venv = env.virtualenv(self.get_path("myenv"))
        self.assertTrue(venv.find_executable("python").startswith(self.tmpdir))

    def test_virtualenv_relative(self):
        """
        Tests if we can create a virtual environment giving a relative path.
        """
        os.chdir(self.tmpdir)
        env = pyenv.interpeter_pyenv()
        venv = env.virtualenv("myenv")
        self.assertTrue(venv.find_executable("python").startswith(self.tmpdir))

    def test_virtualenv_overwrites(self):
        """
        Tests if a virtual env is replacing an existing virtual env.
        """
        env = pyenv.interpeter_pyenv()
        env.virtualenv(self.get_path("myenv"))
        with open(self.get_path("myenv/helloworld"), 'w') as f:
            f.write("content")
        
        env.virtualenv(self.get_path("myenv"))
        
        self.assertFalse(os.path.exists(self.get_path("myenv/helloworld")))

    def test_config(self):
        """
        Test if we can load an environment from a configuration file.
        """
        self.create_files(["python.exe"])

        cfgfile = self.get_path("config.json")
        with open(cfgfile, 'w') as f:
            json.dump({"abc": self.get_path("python.exe")}, f)

        envs = pyenv.from_config(cfgfile)
        self.assertEqual(self.get_path("python.exe"), envs["abc"].find_executable("python"))
 
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
