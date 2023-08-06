import os
from six.moves import range
from types import GeneratorType
from .docdecs import params


@params(path=(str, "Deepest absoulte path to start in"),
        returns=(GeneratorType, "Yields all paths above the given path"))
def backpaths(path):
    """Get all above paths.

    Return a generator of each path that makes up the given path. Essentially
    walking up the tree of directories from the given directory.

    The give path should be an absolute path.
    """
    paths = path.split(os.sep)[1:]
    for i in reversed(range(len(paths) + 1)):
        yield '/' + os.sep.join(paths[:i])


@params(filename=(str, "Filename to be checked for"),
        path=(str, "Absolute path to start in the search in"),
        toroot=(bool, "Step all the way back to root or stop at home"),
        returns=(str, "First filename match backwards from path"))
def backsearch(filename, path, toroot=False):
    """Backwards search for a filename.

    Search for the given `filename` in every directory above the given `path`.
    Returns the first found filename before home or root if toroot is True.
    """
    home = os.getenv("HOME")
    for path in backpaths(path):
        if not toroot and path == home:
            break

        checkpath = os.path.join(path, filename)
        if os.path.exists(checkpath):
            return checkpath
