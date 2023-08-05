"""Uranium, a build system for python

Usage:
  uranium [<uranium_file> -v]
  uranium (-h | --help)

Options:
  -h, --help        show this usage guide
  -v, --verbose     show verbose output

By default, uranium will look for a uranium.yaml
file in the current directory uranium was
invoked in. this can be overridden by passing in a
path to a <uranium_file>
"""
from docopt import docopt
from .uranium import Uranium
from .config import load_config_from_file
import os
import sys

DEFAULT_URANIUM_FILE = "uranium.yaml"


def main(argv=sys.argv[1:]):
    _activate_virtualenv(os.curdir)
    options = docopt(__doc__,  argv=argv)
    uranium_file = options['<uranium_file>'] or DEFAULT_URANIUM_FILE
    uranium = _get_uranium(uranium_file)
    uranium.run()


def _get_uranium(uranium_file):
    root = os.path.abspath(os.curdir)
    config = load_config_from_file(uranium_file)
    return Uranium(config, root)


def _activate_virtualenv(uranium_dir):
    """ this will activate a virtualenv in the case one exists """
    # if the pyvenv launcher environment variable is set, it causes the install directory
    # to be that directory.
    # we want the virtualenv directory to be the one we just created, so we remove
    # this variable
    if '__PYVENV_LAUNCHER__' in os.environ:
        del os.environ['__PYVENV_LAUNCHER__']

    activate_this_path = os.path.join(uranium_dir, 'bin', 'activate_this.py')
    with open(activate_this_path) as fh:
        exec(fh.read(), {'__file__': activate_this_path}, {})
