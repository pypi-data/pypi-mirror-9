from contextlib import contextmanager
from tempfile import mkdtemp
from shutil import rmtree
from nekrobox.docdecs import params


@contextmanager
def tempdir():
    '''This context manager can be used to create a temporary directory
    that will be deleted after the context has ended.
    '''
    path = mkdtemp()
    yield path
    rmtree(path, ignore_errors=True)
