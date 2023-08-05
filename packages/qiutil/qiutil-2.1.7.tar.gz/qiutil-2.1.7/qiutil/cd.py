import os
from contextlib import contextmanager

@contextmanager
def cd(path):
    """
    Safely changes directory in a ``with`` context, e.g.::
    
        from qiutil.cd import cd
        with cd('/path/to/dir'):
            # Do something...  
    
    This :meth:`cd` function is functionally equivalent to the
    `Grizzled <http://software.clapper.org/grizzled-python/>` 
    ``working_directory`` function. It is included in this
    ``qiutil`` package for convenience.
    
    :Note: this :meth:`cd` function is intended for use only
    within a context. Use outside of a context does not change
    the working directory, e.g.:
    
    >> import os
    >> from qiutil.cd import cd
    >> wd = os.getcwd()
    >> cd('/tmp')
    >> os.getcwd() == wd
    True
    
    :param path: the directory path to change to
    """
    prevdir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prevdir)
