import logging
import os
from .bin import BinDirectory
from .cache import Cache, DEFAULT_CACHE_DIRECTORY
from .classloader import ClassLoader
from .config import Config
from .messages import START_URANIUM, END_URANIUM
from .parts import PartRunner
from .phases import (AFTER_EGGS, BEFORE_EGGS)
from .pip_manager import PipManager
from .state import State
LOGGER = logging.getLogger(__name__)


class UraniumException(Exception):
    pass

BIN_DIRECTORY = "bin"
PARTS_DIRECTORY = "parts"


class Uranium(object):

    def __init__(self, config, root, state_file=None):
        # well cast the dict to a config for people
        # to make it easier
        if type(config) == dict:
            config = Config(config)

        self._cache = Cache(os.path.join(root, DEFAULT_CACHE_DIRECTORY))
        self._root = root
        self._config = config
        self._pip = PipManager(index_urls=self._config.indexes,
                               # this is a lambda to ensure we always
                               # pick up a newly resolved version
                               versions=lambda: self.config.resolved_versions)
        self._classloader = ClassLoader(self._pip)
        self._state = State(state_file)
        self._environment = {}
        self._environment.update(config.envs)
        self._part_runner = PartRunner(self, self._classloader)
        self._validate_config()

    @property
    def config(self):
        return self._config

    @property
    def root(self):
        return self._root

    @property
    def state(self):
        return self._state

    @property
    def bin(self):
        if not hasattr(self, '_bin'):
            self._bin = BinDirectory(
                os.path.join(self._root, BIN_DIRECTORY))
        return self._bin

    @property
    def environment(self):
        """
        environment is the dictionary that can be used to set environment
        variables.

        any key/value pairs set here will be injected into the
        initialization scripts.
        """
        return self._environment

    @property
    def parts_directory(self):
        return os.path.join(self.root, PARTS_DIRECTORY)

    def run(self):
        self._cache.ensure_directory()
        self._state.load()
        [LOGGER.info(l) for l in START_URANIUM]

        self._create_bin_directory()
        self.run_phase(BEFORE_EGGS)
        LOGGER.info("installing eggs...")
        self._install_eggs()
        self.run_phase(AFTER_EGGS)

        [LOGGER.info(l) for l in END_URANIUM]
        self._state.save()

    def run_phase(self, phase):
        LOGGER.debug("running phase {0}...".format(phase.key))
        part_names = self._config.phases.get(phase.key, [])
        for name in part_names:
            self.run_part(name)

    def run_part(self, name):
        self._part_runner.run_part(name)

    def _create_bin_directory(self):
        bin_directory = os.path.join(self._root, 'bin')
        if not os.path.exists(bin_directory):
            os.makedirs(bin_directory)

    def _install_eggs(self):
        develop_eggs = self._config.get('develop-eggs')
        if develop_eggs:
            errors = self._pip.add_develop_eggs(develop_eggs)
            for egg_path, error in errors:
                msg = "WARNING: Unable to install develop egg at {0}: {1}".format(
                    egg_path, error
                )
                LOGGER.warning(msg)
        # for some reason install can only be run once
        # it seems to be related to the packages being installed,
        # then attempting to install them again with the same
        # packagemanager
        # self._pip.install()

        eggs = self._config.get('eggs')
        if eggs:
            self._pip.add_eggs(eggs)
        self._pip.install()

    def _validate_config(self):
        warnings, errors = self._config.validate()
        for warning in warnings:
            LOGGER.warn(warning)
        if errors:
            for error in errors:
                LOGGER.error(error)
            raise UraniumException("uranium.yaml is not valid.")
