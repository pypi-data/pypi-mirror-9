from setuptools import setup, find_packages

from filehandle import __version__

setup(
    name = 'filehandle',
    version = __version__,
    py_modules = ['filehandle'],
    setup_requires = [
        'nose',
        'python-coveralls'
    ],
    tests_require = [
    ],
    entry_points = {
    },
    install_requires = [],
    author = 'Tyghe Vallard',
    author_email = 'vallardt@gmail.com',
    description = 'Normalize the way you get a file handle from either gzip or normal file',
    license = 'GPL v2',
    keywords = 'gzip, handle, open, file',
    url = 'https://github.com/necrolyte2/filehandle',
)
