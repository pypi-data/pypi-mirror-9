import os


def which(program):
    """
    Returns the file path of the first executable of the given program
    name in the system ``PATH`` environment variable.
    
    This function is a system-independent Python equivalent of the \*nix
    ``which`` command.
    
    :Note: The implementation is adapted from
        http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python.
    
    :param program: the program name to check
    :return: the filename in the system path
    """
    fpath, fname = os.path.split(program)
    if fpath:
        if _is_executable(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if _is_executable(exe_file):
                return exe_file

    return None


def _is_executable(fpath):
    """
    :param fpath: the file path to check
    :return: whether the file exists and is executable
    """
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
