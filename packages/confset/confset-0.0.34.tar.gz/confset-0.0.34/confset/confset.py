#!/usr/bin/env python
"""
Manage package settings
"""
import os
import sys
import shutil
import time
import logging


CONF_PATH = ['/etc/default', '/etc/sysconfig']
METADATA_DIR = '/etc/confset'
logger = logging.getLogger(__name__)


class ConfsetException(Exception):
    pass


class ConfigSettings(object):
    """
    Configuration settings class
    :param conffile:
    """

    def __init__(self, conffile=None):
        self.confpath = config_paths()
        self.conffile = conffile
        self.filename = self.search_for_conf(conffile)
        self.settings, self.order = self.available_settings()
        self.__dict__.update(self.settings)

    # noinspection PyMethodMayBeStatic
    def search_for_conf(self, conffile):
        """
        Search for a configuration file
        :param conffile:
        :return:
        """
        filename = None
        for d in self.confpath:
            filename = os.path.join(d, self.conffile)
            if os.path.isfile(filename) and os.access(filename, os.R_OK):
                break
            else:
                filename = None
        return filename

    def empty_conf_file(self):
        """
        Return a fully filename
        :return:
        """
        for d in self.confpath:
            if os.path.isdir(d) and os.access(d, os.W_OK):
                return os.path.join(d, self.conffile)
        raise ConfsetException(
            'Unable to find a writable configuration directory'
        )

    def available_settings(self):
        """
        Return the settings available in a conf file
        :return:
        """
        comments = []
        order = []
        result_settings = {}
        if self.filename:
            fh = open(self.filename, 'r')
            for line in fh.readlines():
                line = line.strip()
                if line:
                    if line.startswith('#'):
                        temp = line.strip('#').strip()
                        if temp:
                            comments.append(temp)
                    else:
                        if '=' in line:
                            setting = '%s.%s' % (
                                self.conffile, line.split('=')[0])
                            result_settings[setting] = {
                                'help': comments,
                                'value': '='.join(line.split('=')[1:]).strip()
                            }
                            comments = []
                            order.append(setting)
                else:
                    comments = []
        return result_settings, order

    def key_max_column_width(self):
        """
        Determine the max length of the key names
        :return:
        """
        max_len = 1
        for setting in self.settings.keys():
            if len(setting) + len(self.settings[setting]['value']) + 1 > max_len:
                max_len = len(setting) + len(
                    self.settings[setting]['value']) + 1
        return max_len

    def print_settings(
            self, setting_filter=None, sort=False, key_column_width=None,
            info=None
    ):
        """
        Print the current settings
        :param info:
        :param key_column_width:
        :param setting_filter:
        :param sort:
        """
        if sort:
            temp = self.settings.keys()
            temp.sort()
        else:
            temp = self.order

        if key_column_width:
            max_len = key_column_width
        else:
            max_len = self.key_max_column_width()

        for setting in temp:
            if not setting_filter or setting == setting_filter.strip():
                setting_and_value = '%s=%s' % (
                    setting,
                    self.settings[setting]['value']
                )
                if info and self.settings[setting]['help']:
                    print(
                        '%s - %s' % (
                            setting_and_value.ljust(max_len, ' '),
                            self.settings[setting]['help'][0] if self.settings[setting]['help'] else ''
                        )
                    )
                    for line in self.settings[setting]['help'][1:]:
                        print('%s   %s' % ((' ' * max_len), line))
                else:
                    if self.settings[setting]['value']:
                        print(setting_and_value)

    def set(self, key, value, help=None):
        """
        Set a setting in a conf file
        :param key:
        :param value
        """
        if not help:
            help = []
        if not self.filename:
            self.filename = self.empty_conf_file()
        if os.path.exists(self.filename):
            shutil.copy(self.filename, '%s.confset.%s' % (
                self.filename, time.strftime("%Y%m%d%H%M%S"))
            )
            data = open(self.filename, 'r').readlines()
        else:
            data = []
        changed = False
        fh = open(self.filename, 'w')
        for line in data:
            if not line.strip().startswith('#') and '=' in line:
                tkey = line.strip().split('=')[0].strip()
                # noinspection PyUnusedLocal
                tvalue = line.strip().split('=')[1].strip()
                if key == tkey:
                    line = ''
                    if help:
                        line = '# %s\n' % help
                    line += '%s=%s\n' % (key, value)
                    changed = True
            fh.write(line)
        if not changed:
            fh.write('%s=%s\n' % (key, value))

        self.settings.update(
            {
                '%s.%s' % (self.conffile, key): {
                    'help': help,
                    'value': value}
            }
        )
        fh.close()


def config_paths():
    """
    Get a list of configuration paths
    :return:
    """
    global CONF_PATH
    confpath = CONF_PATH
    if hasattr(sys, 'real_prefix') and 'VIRTUAL_ENV' in os.environ.keys():
        confpath.insert(
            0,
            os.path.join(
                os.environ['VIRTUAL_ENV'],
                'conf'
            )
        )
    return confpath


def config_files():
    """
    Find all config files
    :return:
    """
    files = []
    for directory in config_paths():
        if os.path.isdir(directory):
            for f in os.listdir(directory):
                if '.confset.' not in f:
                    files.append(f)
    return files


def settings():
    """
    Return all settings as a dictionary
    :return:
    """
    all_settings = {}
    for f in config_files():
        try:
            conf = ConfigSettings(os.path.basename(f))
        except IOError as exc:
            logger.debug(
                'Got %s while getting config settings for %s',
                exc,
                os.path.basename(f)
            )
            continue
        s, o = conf.available_settings()
        all_settings.update(s)
    return all_settings


def print_settings(setting_filter=None, info=False):
    """
    Print settings found
    :param setting_filter:
    :param info:
    """
    configs = []
    max_width = 1
    for f in config_files():
        try:
            conf = ConfigSettings(os.path.basename(f))
        except IOError as exc:
            logger.debug(
                'Got %s while getting config settings for %s',
                exc, os.path.basename(f)
            )
            continue
        if conf.key_max_column_width() > max_width:
            max_width = conf.key_max_column_width()
        configs.append(conf)
    for conf in configs:
        conf.print_settings(
            setting_filter=setting_filter,
            key_column_width=max_width,
            info=info
        )
