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

import os.path
import sys
import shutil
import subprocess
import json

class PyEnv(object):
    """
    Represents a python environment.
    An environment consists of a python interpeter, python library paths and utilities such as `pip`.
    Currenty we are only concerned about the paths were we find the interpeter and the utilities.
    """

    def __init__(self, search_paths):
        """
        Manually configure an enviroment.
        You might want to consider using the factory methods provided in this module.
        """
        self.search_paths = search_paths
        self.exec_patterns = ['{name}' ,'{name}.exe']
        self.python_patterns = ['{name}', 'w{name}.exe' ,'{name}.exe']


    def __getattr__(self, name):
        """
        Returns a method that invokes an exectuable in this environment.
        Arguments passed to the method become console line arguments.
        """
        executable = self.find_executable(name)
        
        def invoker(*args):
            subprocess.check_call([executable] + list(args))
        return invoker


    def virtualenv(self, path="env", system_side_packages=False):
        """
        Creates a new virtual environment and returns the PyEnv for it.
        
        :param path: Location of the virtual environment. Can be an
            absolute path or a path relative to the current directory.
            Defaults to `"env"`.
            
        :param system_side_packages: Should the venv see the packages
            of the main environment?

        :returns: PyEnv instance for the new environment.
        """
        abspath = os.path.abspath(path)
        
        if os.path.isdir(abspath):
            shutil.rmtree(abspath)
        elif os.path.exists(abspath):
            os.remove(abspath)
        
        parent = os.path.dirname(abspath)
        if not os.path.exists(parent):
            os.makedirs(parent)
        
        currentdir = os.getcwd()
        try:
            os.chdir(parent)
            
            virtualenv = self.find_executable("virtualenv")
            args = [virtualenv, os.path.basename(abspath)]
            if system_side_packages:
                args.append("--system-site-packages")
            subprocess.check_call(args)

            return from_virtualenv(abspath)

        finally:
            os.chdir(currentdir)


    def find_executable(self, name):
        """
        Finds an executable with the given name in this enviroment.
        
        :returns: Absolute path to the executable.

        :raises ValueError: if the exectuable could not be found.
        """
        
        patterns = self.python_patterns if name == "python" else self.exec_patterns
        candidate_names = [ext.format(name=name) for ext in patterns]
        candidates = [os.path.join(path, name) for path in self.search_paths for name in candidate_names]
   
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
            
        raise ValueError("Unable to find {name}. Looked at {candidates}".format(
            name=repr(name),
            candidates=", ".join(candidates)
        ))
        

def interpeter_pyenv():
    """
    Returns the environment in which this script is running.
    """
    if not sys.executable:
        raise ValueError("Interpeter that runs this script cannot be identified.")
    return from_interpreter(sys.executable)


def from_config(*search_paths):
    """
    Reads a json file with a `{name:"path/to/python", ...}` content and
    returns a `dict` with the names and :class:`PyEnv` instances for each
    entry.

    By default it searches in the following locations (in that order):

    * ./cish.json
    * ${HOME}/cish.json  (or its windows equivalent)
    * /etc/cish.json (linux, osx)
    * C:\cish.json (windows)

    Additional paths can be given as arguments and are searched before
    falling back to the default paths.
    """

    filename = "cish.json"

    paths = list(search_paths)
    paths.append(os.path.abspath(filename))
    paths.append(os.path.join(os.path.expanduser("~"), filename))
    if os.name == "nt":
        paths.append("C:\\" + filename)
    else:
        paths.append(os.path.sep + os.path.join("etc", filename))

    for path in paths:
        if os.path.exists(path):
            config_file = path
            break
    else:
        raise ValueError("Unable to locate configuration file. Searched in {paths}".format(
            paths = ", ".join(paths)))

    with open(config_file, 'r') as f:
        config = json.load(f)

    if not hasattr(config, "iteritems"):
        raise ValueError("Invalid config file {f}. Must contain a key-value dict " + 
            "as the top level element.".format(f=config_file))

    return dict((name, from_interpreter(exe)) for name, exe in config.iteritems())


def from_interpreter(exe):
    """
    Attempts to construct the environment for a given python interpeter by guessing
    where the paths are relative to it.
 
    :param exe: Path to the python interpeter executable.
 
    :returns: Instance of :class:`PyEnv`
    """
    exeabs = os.path.abspath(exe)
    if not os.path.exists(exeabs):
        raise ValueError("Python interpreter {exe} does not exist here {exeabs}.".format(exe=exe, exeabs=exeabs))
    
    path = os.path.dirname(exeabs)
    return _from_paths(path, ["Scripts", "scripts"])


def from_virtualenv(path):
    """
    Attempts to construct the environment from the directory created by `virtualenv`.
    
    :param path: Directory containing the virtualenv.

    :returns: Instance of :class:`PyEnv`
    """
    return _from_paths(path, ["bin", "Scripts", "scripts"])    


def _from_paths(path, subdirs):
    """
    Helper method to construct an environment.

    :param path: Base path of the environment.

    :param subdirs: Directory names that might contain the interpeter and utilities.

    :returns: Instance of :class:`PyEnv`
    """
    paths = [path] + [os.path.join(path, subdir) for subdir in subdirs]
    search_paths = []
    for path in paths:
        if os.path.isdir(path): 
            search_paths.append(path)
    if not search_paths:
        raise ValueError("Python environment not found. None of the directories exists {dirs}".format(
            dirs=", ".join(paths)))
    return PyEnv(search_paths)

