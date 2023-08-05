from setuptools import setup

long_desc = """\
NetworkX can use pydot for GraphViz support, but pydot doesn't support
Python 3.

This package creates a wrapper around pydotplus, a Python 3 compatible
version of pydot, making it look like pydot.

Note that nxpydot installs top level modules "pydot" and "dot_parser",
which clash with pydot. So don't install this if you have pydot.
"""

setup(
    name="nxpydot",
    version='0.1',
    description="Wrapper round pydotplus to make it work with NetworkX",
    long_description=long_desc,

    url='http://github.com/pfmoore/nxpydot',

    author='Paul Moore',
    author_email='p.f.moore@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='graphviz dot graphs visualization',
    py_modules = ['pydot', 'dot_parser'],
    install_requires = ['pydotplus'],
)
