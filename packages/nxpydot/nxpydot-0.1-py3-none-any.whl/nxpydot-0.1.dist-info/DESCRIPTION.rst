NetworkX can use pydot for GraphViz support, but pydot doesn't support
Python 3.

This package creates a wrapper around pydotplus, a Python 3 compatible
version of pydot, making it look like pydot.

Note that nxpydot installs top level modules "pydot" and "dot_parser",
which clash with pydot. So don't install this if you have pydot.


