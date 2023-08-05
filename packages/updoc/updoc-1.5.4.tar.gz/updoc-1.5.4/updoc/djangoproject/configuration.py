#coding=utf-8
from configparser import ConfigParser, _UNSET
import os

__author__ = 'flanker'


class ConfigurationParser(ConfigParser):
    
    def __init__(self, *args):
        super().__init__(*args)
        self.__used_options = {}
        self.__read_filenames = []
        self.__help_texts = {}

    def __store(self, section, option, value):
        self.__used_options.setdefault(section, {})[option] = str(value) if value is not None else ''
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, option, str(value) if value is not None else '')
        return value

    # noinspection PyMethodOverriding
    def get(self, section, option, raw=False, vars=None, fallback=_UNSET, help_text=None):
        result = super().get(section, option, raw=raw, vars=vars, fallback=fallback)
        if help_text:
            self.__help_texts.setdefault(section, {})[option] = help_text
        return self.__store(section, option, result)

    # noinspection PyMethodOverriding
    def getboolean(self, section, option, raw=False, vars=None, fallback=_UNSET, help_text=None):
        result = super().getboolean(section, option, raw=raw, vars=vars, fallback=fallback)
        if help_text:
            self.__help_texts.setdefault(section, {})[option] = help_text
        return self.__store(section, option, result)

    # noinspection PyMethodOverriding
    def getint(self, section, option, raw=False, vars=None, fallback=_UNSET, help_text=None):
        result = super().getint(section, option, raw=raw, vars=vars, fallback=fallback)
        if help_text:
            self.__help_texts.setdefault(section, {})[option] = help_text
        return self.__store(section, option, result)

    @property
    def used_options(self):
        return self.__used_options

    def read(self, filenames, encoding=None):
        super().read(filenames, encoding=encoding)
        self.__read_filenames += [os.path.abspath(x) for x in filenames]

    @property
    def read_filenames(self):
        return self.__read_filenames
    

if __name__ == '__main__':
    import doctest

    doctest.testmod()