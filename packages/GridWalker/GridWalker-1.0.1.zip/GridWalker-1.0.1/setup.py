import os
from setuptools import setup

def read(fname):
    with open(fname) as fhandle:
        return fhandle.read()

def readMD(fname):
    # Utility function to read the README file.
    full_fname = os.path.join(os.path.dirname(__file__), fname)
    if 'PANDOC_PATH' in os.environ:
        import pandoc
        pandoc.core.PANDOC_PATH = os.environ['PANDOC_PATH']
        doc = pandoc.Document()
        with open(full_fname) as fhandle:
            doc.markdown = fhandle.read()
        return doc.rst
    else:
        return read(fname)

required = [req.strip() for req in read('requirements.txt').splitlines() if req.strip()]
version = '1.0.1'
setup(
    name='GridWalker',
    version=version,
    author='Matthew Seal',
    author_email='mseal@opengov.com',
    description='A multi-dimensional grid used for state space searching',
    long_description=readMD('README.md'),
    install_requires=required,
    license='New BSD',
    packages=['gridwalker'],
    test_suite='tests',
    zip_safe=False,
    url='https://github.com/OpenGov/grid_walker',
    download_url='https://github.com/OpenGov/grid_walker/tarball/v' + version,
    keywords=['grids', 'data', 'iterator', 'multi-dimensional'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2 :: Only'
    ]
)
