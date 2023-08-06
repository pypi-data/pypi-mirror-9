import logging
import os
import re
import subprocess
from virtualenv import create_environment

LOGGER = logging.getLogger(__name__)


def install_virtualenv(install_dir):
    if is_virtualenv(install_dir):
        return

    create_environment(install_dir, no_setuptools=False,
                       no_pip=True, site_packages=False,
                       symlink=False)


VIRTUALENV_FILES = {
    'activate file': os.path.join('bin', 'activate')
}


def is_virtualenv(path):
    """ validate if the path is already a virtualenv """
    for name, venv_path in VIRTUALENV_FILES.items():
        target_path = os.path.join(path, venv_path)
        if not os.path.exists(target_path):
            return False
    return True

INJECT_WRAPPER = "# URANIUM_INJECT THIS"

INJECT_MATCH = re.compile("(\n?{0}.*{0}\n)".format(INJECT_WRAPPER), re.DOTALL)

INJECT_TEMPLATE = """
{0}
{{body}}
{0}
""".format(INJECT_WRAPPER)

SITE_PY_INJECTION = """
# reshuffling the paths to ensure that distributions in the sandbox
# always come first
paths_to_append = [p for p in sys.path if p.startswith(sys.real_prefix)]
sys.path = [p for p in sys.path if not p.startswith(sys.real_prefix)]
sys.path += paths_to_append
"""


def inject_into_activate_this(venv_root, body):
    """
    inject a body into activate_this.py.

    this will overwrite any values previously injected into activate_this.
    """
    activate_this_file = os.path.join(venv_root, 'bin', 'activate_this.py')
    inject_into_file(activate_this_file, body)


def inject_sitepy(venv_root):
    site_py_file = _get_site_file_path(venv_root)
    inject_into_file(site_py_file, SITE_PY_INJECTION)


def _get_site_file_path(venv_directory):
    executable = os.path.join(venv_directory, 'bin', 'python')
    return subprocess.Popen(
        [executable, "-c", "import site; print(site.__file__)"],
        stdout=subprocess.PIPE
    # we strip the last character 'c' in case it's a .pyc file
    # want the .py
    ).communicate()[0].decode('utf-8').rstrip('c\n')


def inject_into_file(path, body):
    """ inject into a file """
    with open(path) as fh:
        content = fh.read()

    content = INJECT_MATCH.sub("", content)
    content += INJECT_TEMPLATE.format(body=body)

    with open(path, 'w+') as fh:
        fh.write(content)
