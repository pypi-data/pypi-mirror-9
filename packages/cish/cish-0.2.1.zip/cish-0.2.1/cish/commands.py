import os.path
import shutil

def pwd():
    """
    Returns the current working directory.
    This is just a convinience function to access `os.getcwd()`.
    """
    return os.getcwd()


def cd(path):
    """
    Change the current directory.

    The return value can be used with the `with` statement to 
    automatically switch back to the previous directory like this::

        with cish.cd("subdir"):
            print cish.pwd()  # we are inside "subdir"
        print cish.pwd()      # we are back where we were before.
           
    The new absolute path of the current directory can also be
    obtained using the `with .. as` statement::

        with cish.cd("subdir") as path:
            print path        # we are inside "subdir"
        print cish.pwd()      # we are back where we were before.

    This produces the same output as the previous example.
    """
    path = os.path.abspath(path)
    prev_pwd = os.getcwd()

    # Don't wait for __enter__ as this function might not be
    # used with `with`.
    os.chdir(path)

    class ChangeDirContext(object):
        def __enter__(self):
            return path
        
        def __exit__(self, type_, value, traceback):
            os.chdir(prev_pwd)
            return False # re-throw exceptions if there was one.

    return ChangeDirContext()


def mkdirs(path):
    """
    Creates the given directory, creating parent directories if required.
    Has no effect if the directory already exists, throws an exception
    if the path exists but is not a directory.
    """
    path = os.path.abspath(path)
    if os.path.isdir(path):
        return
    elif os.path.exists(path):
        raise ValueError("Cannot create directory {path} it already exists " +
             "but is not a directory.".format(path=path))
    else:
        os.makedirs(path)


def rm(path):
    """
    Deletes the given file or directory, including the content.
    Has no effect if the path does not exist.
    """
    path = os.path.abspath(path)
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


