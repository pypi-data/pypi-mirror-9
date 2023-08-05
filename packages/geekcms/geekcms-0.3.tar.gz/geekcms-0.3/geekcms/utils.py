
"""
This package implements tools that can facilitates theme development.
"""

import os
import re
import sys
import configparser
from collections import abc
from functools import wraps

from .protocol import PluginRegister


class SettingsLoader:

    PROJECT_GLOBAL = 'global'

    def __init__(self, path, name=None):
        # settings of project has 'global' as its prefix.
        self.name = name or self.PROJECT_GLOBAL
        # check and save path
        if not os.path.exists(path):
            raise Exception('{} Not Exists.'.format(path))
        self.path = path
        # load up
        self._load_settings()

    def _load_settings(self):
        config = configparser.ConfigParser()
        with open(self.path) as f:
            config.read_file(f)
        self._config = config

    def get_section(self, section):
        if section in self._config:
            return self._config[section]
        else:
            return None


class _SearchData:

    DATA_FIELD = None

    @classmethod
    def load_data(cls, loaders):
        # ensure iterable
        if not isinstance(loaders, abc.Iterable):
            loaders = [loaders]
        for loader in loaders:
            section = loader.get_section(cls.DATA_FIELD)
            if section:
                cls._vars[loader.name] = section

    @classmethod
    def clear(cls):
        cls._vars.clear()
        cls._cache.clear()

    @classmethod
    def _access_vars(cls, section_name, key):
        section = cls._vars.get(section_name, None)
        if section:
            val = section.get(key, None)
            return val
        else:
            return None

    @classmethod
    def _generate_key_val_of_vars(cls):
        for section_name, section in cls._vars.items():
            for key, val in section.items():
                yield key, val

    @classmethod
    def _get_cache(cls, key):
        return getattr(cls._cache, key, None)

    @classmethod
    def _set_cache(cls, key, val):
        cls._cache[key] = val

    @classmethod
    def get(cls, search_key):
        # anyway, lookup the cache first.
        val = cls._get_cache(search_key)
        if val:
            return val

        # First way.
        dot_index = search_key.find('.')
        if dot_index != -1 and dot_index != (len(search_key) - 1):
            # prefix with theme name or global.
            section_name = search_key[:dot_index]
            key = search_key[dot_index + 1:]
            val = cls._access_vars(section_name, key)
            if val:
                cls._set_cache(search_key, val)
                return val
        # Second way.
        for key, val in cls._generate_key_val_of_vars():
            if search_key == key:
                cls._set_cache(search_key, val)
                return val
        return None


class ShareData(_SearchData):

    DATA_FIELD = 'Share'
    _vars = {}
    _cache = {}


class ProjectSettings(_SearchData):

    DATA_FIELD = 'RegisterTheme'
    _vars = {}
    _cache = {}

    @classmethod
    def get_registered_theme_name(cls):
        THEMES_KEY = 'themes'
        plain_text = cls.get(THEMES_KEY)
        # yep, name of themes is split by whitespaces.
        theme_names = re.split(r'\s+', plain_text)
        # remove empty string.
        return [name for name in theme_names if name]


class ThemeSettings(_SearchData):

    DATA_FIELD = 'RegisterPlugin'
    _vars = {}
    _cache = {}


class PathResolver:

    INPUTS = 'inputs'
    OUTPUTS = 'outputs'
    THEMES = 'themes'
    STATES = 'states'

    PROJECT_SETTINGS = 'settings'
    THEME_SETTINGS = 'settings'

    project_path = None

    def _let_dir_exist(func):
        @wraps(func)
        def func_with_option(*args, ensure_exist=False, **kwargs):
            path = func(*args, **kwargs)
            if ensure_exist and not os.path.exists(path):
                os.makedirs(path)
            return path
        return func_with_option

    def _let_file_exist(func):
        @wraps(func)
        def func_with_option(*args, ensure_exist=False, **kwargs):
            path = func(*args, **kwargs)
            if ensure_exist and not os.path.exists(path):
                open(path, 'a').close()
            return path
        return func_with_option

    @classmethod
    def set_project_path(cls, path):
        cls.project_path = path

    @classmethod
    def _join_project(cls, path):
        return os.path.join(cls.project_path, path)

    @classmethod
    @_let_dir_exist
    def inputs(cls):
        return cls._join_project(cls.INPUTS)

    @classmethod
    @_let_dir_exist
    def outputs(cls):
        return cls._join_project(cls.OUTPUTS)

    @classmethod
    @_let_dir_exist
    def themes(cls):
        return cls._join_project(cls.THEMES)

    @classmethod
    @_let_dir_exist
    def states(cls):
        return cls._join_project(cls.STATES)

    @classmethod
    @_let_dir_exist
    def theme_state(cls, theme_name):
        return os.path.join(
            cls.states(),
            theme_name,
        )

    @classmethod
    @_let_dir_exist
    def theme_dir(cls, theme_name):
        return os.path.join(
            cls.themes(),
            theme_name,
        )

    @classmethod
    @_let_file_exist
    def project_settings(cls):
        return cls._join_project(cls.PROJECT_SETTINGS)

    @classmethod
    @_let_file_exist
    def theme_settings(cls, theme_name):
        return os.path.join(
            cls.theme_dir(theme_name),
            cls.THEME_SETTINGS,
        )


class SysPathContextManager:

    def __init__(self, theme_name, theme_dir):
        self.theme_name = theme_name
        self.path = theme_dir

    def __enter__(self):
        sys.path.insert(0, self.path)
        PluginRegister.context_theme = self.theme_name

    def __exit__(self, *args):
        sys.path.remove(self.path)
        PluginRegister.unset_context_theme()


class PathResolverContextManager:

    def __init__(self, path=None):
        self.path = path

    def __enter__(self):
        self.bak_path = PathResolver.project_path
        PathResolver.set_project_path(self.path)

    def __exit__(self, *args):
        PathResolver.set_project_path(self.bak_path)


def check_cwd_is_project():

    require_exist_path = [
        PathResolver.inputs(),
        PathResolver.outputs(),
        PathResolver.themes(),
        PathResolver.states(),
        PathResolver.project_settings(),
    ]

    for requied_path in require_exist_path:
        if not os.path.exists(requied_path):
            return False
    return True
