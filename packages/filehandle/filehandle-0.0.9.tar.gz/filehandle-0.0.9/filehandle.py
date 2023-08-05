import gzip
from os.path import splitext

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

__version__ = '0.0.9'

def open(filepath, mode='rb', buffcompress=None):
    '''
    Open a file based on the extension of the file
    if the filepath ends in .gz then use gzip module's open otherwise
    use the normal builtin open

    :param str filepath: Path to .gz or any other file
    :param str mode: mode to open file
    :param int buffcompress: 3rd option for builtin.open or gzip.open
    :return: tuple(filehandle, fileextension)
    '''
    root, ext = splitext(filepath.replace('.gz', ''))
    # get rid of period
    ext = ext[1:]
    if filepath.endswith('.gz'):
        compress = buffcompress
        if compress is None:
            compress = 9
        handle = gzip.open(filepath, mode, compress)
    else:
        buffer = buffcompress
        if buffer is None:
            buffer = -1
        handle = builtins.open(filepath, mode, buffer)
    return (handle, ext)
