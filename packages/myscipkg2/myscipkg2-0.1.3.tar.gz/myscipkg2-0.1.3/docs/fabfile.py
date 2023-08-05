# :title: fabfile.py
# :author: John A. Marohn (jam99@cornell.edu)
# :date: 2014-07-26
# :subject: substitute/extend "make html" and "make open"
# :ref: http://docs.fabfile.org/en/1.4.1/tutorial.html
# :ref: http://ipython.org/ipython-doc/1/interactive/nbconvert.html

from fabric.api import *
from fabric.context_managers import lcd
import os
import glob
import webbrowser

env.ipython_dir = os.path.join(os.path.join('..', 'freqdemod'), 'docs')
home = os.getcwd()


def help():
    """Print out a helpful message."""

    print("""\
====================================================================
fab clean      Delete the contents of the _build/ directory
fab html       Create sphinx documentation as stand-alone HTML files
fab html_full  Convert the ipynb files in the ../freqdemod/docs
               dir to HTML files, then create sphinx documentation
               as stand-alone HTML files")
open           Open the HTML documentation in a web browser
====================================================================""")


def clean():
    """Delete the contents of the _build/ directory."""

    local('rm -rf _build/*')


def html_full():
    """
    Convert the ipynb files in the ../freqdemod/doc dir to HTML files, then
    create sphinx documentation as stand-alone HTML files.
    """

    os.chdir(os.path.join('{ipython_dir}'.format(**env)))
    ipynb_files = glob.glob('*.ipynb')
    os.chdir(home)

    with lcd('{ipython_dir}'.format(**env)):
        for file in ipynb_files:
            print('{}'.format(file))
            local('ipython nbconvert --to html --template full {}'.format(file))

    with lcd(''):
        local('sphinx-build -b html . _build/html')

    print("Build finished; see _build/html/index.html")


def html():
    """Create sphinx documentation as stand-alone HTML files."""

    local('sphinx-build -b html . _build/html')
    print("Build finished; see _build/html/index.html")


def open():
    """Open the HTML documentation in a cross-platform way."""
    index_path = "file://{cwd}/_build/html/index.html".format(cwd=home)
    webbrowser.open(index_path)
