
cish - Write shell-like python scripts to control continuous builds
===================================================================

I used to write small bash scripts that created the virtualenv and
executed the `python setup.py` and `nosetests` commands using
one of several Python versions I keep installed on my build machines. 
But bash scripts aren't supported on Windows, so I want to write
this script in Python instead. 

`cish` is a set of utility functions to write bash-like python
scripts that deal with several installed python interpreters.

----------------
Let's get going!
----------------

.. code-block:: python

    import cish
    cish.rm("build")
    cish.default.pip("install", "nose")
    cish.default.python("setup.py", "build")
    cish.default.nosetests()

This will delete the `build` directory if it exists with all content,
install `nose`, and build and test the package.

`default` is an 'environment' which consists of a python interpreter,
library path, and utilities such as `pip`. `default` is the environent
of the interpreter executing the script itself.

We can also use a different interpreter:

.. code-block:: python

    import cish
    env = cish.from_interpreter("path/to/python")
    env.python("setup.py", "build")
    env.nosetests()

The installation location of the python interpreters is often
dependent on the test machine. We can place a simple JSON file
in one of several locations, for example in `/etc/cish.json`, 
to specifiy their location:

.. code-block:: json

    {
        "2.6.9": "/opt/python2.6.9/bin/python",
        "2.7.8": "/opt/python2.7.8/bin/python"
    }

We can then choose the interpeter in our script using, say,
an environment variable set by jenkins:

.. code-block:: python

    import cish, os
    env = cish.from_config()[os.environ["PYTHON_VERSION"]]
    env.python("setup.py", "build")

`virtualenv` is very easy too:

.. code-block:: python

    import cish
    venv = cish.default.virtualenv("optional/location")
    venv.pip("install", "package_to_install_inside_virtualenv")

-----------------------------------
Bug Reports and other contributions
-----------------------------------

This project is hosted here `cish github page <https://github.com/smurn/cish>`_.
 
------------
Alternatives
------------

You might want to look at `sh <https://pypi.python.org/pypi/sh>`_ a cool library to
run executables without dealing with `subprocess` directly. It has a far wider
scope than `cish` but lacks the abstraction we offer for different python installations
and OS specific file extensions and installation locations.

 
