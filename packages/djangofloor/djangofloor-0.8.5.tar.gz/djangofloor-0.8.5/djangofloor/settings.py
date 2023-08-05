# coding=utf-8
""" Django settings for DjangoFloor.

Settings come from 3 modules:

  * djangofloor.defaults
  * project-specific settings, defined in the environment variable DJANGOFLOOR_PROJECT_SETTINGS
  * user-specific settings, defined in the environment variable DJANGOFLOOR_USER_SETTINGS

djangofloor.defaults settings are overridden by project-specific settings, which are of course overridden by
    user-specific settings.

Only variables in uppercase (like INSTALLED_APPS) are taken into account.
Only variables defined in djangofloor.defaults or in project-specific settings are taken into account.

If VARIABLE is uppercase and if VARIABLE_HELP exists, then VARIABLE is shown with command `manage.py config`.

"""
import os
import string
import sys
from django.utils.importlib import import_module
from pathlib import Path
from djangofloor import defaults as floor_settings
from djangofloor import __version__ as version
from djangofloor.utils import DirectoryPath, FilePath


__author__ = 'flanker'

PROJECT_SETTINGS_MODULE_NAME = os.environ.get('DJANGOFLOOR_PROJECT_SETTINGS', '')
USER_SETTINGS_PATH = os.environ.get('DJANGOFLOOR_USER_SETTINGS', '')
PROJECT_NAME = os.environ.get('DJANGOFLOOR_PROJECT_NAME', 'djangofloor')


if not PROJECT_SETTINGS_MODULE_NAME:
    print('"DJANGOFLOOR_PROJECT_SETTINGS" environment variable should be set to the '
          'dotted path of your project defaults')
else:
    print('DjangoFloor version %s, using %s as project defaults' % (version, PROJECT_SETTINGS_MODULE_NAME))


def import_file(filepath, messages=None):
    """import the Python source file as a Python module.

    :param filepath: absolute path of the Python module
    :type filepath: :class:`str`
    :param messages: tuple of three messages:
        (filepath is not given, filepath is given but does not exist, filepath is given and exists)
    :return:
    """
    if filepath and os.path.isfile(filepath):
        dirname = os.path.dirname(filepath)
        if dirname not in sys.path:
            sys.path.insert(0, dirname)
        conf_module = os.path.splitext(os.path.basename(filepath))[0]
        if messages:
            print(messages[2])
        module_ = import_module(conf_module)
    elif filepath:
        if messages:
            print(messages[1])
        import djangofloor.empty
        module_ = djangofloor.empty
    else:
        if messages:
            print(messages[0])
        import djangofloor.empty
        module_ = djangofloor.empty
    return module_

if PROJECT_SETTINGS_MODULE_NAME:
    project_settings = import_module(PROJECT_SETTINGS_MODULE_NAME)
else:
    import djangofloor.empty
    project_settings = djangofloor.empty
user_settings = import_file(USER_SETTINGS_PATH,
                            ('No specific settings file defined in DJANGOFLOOR_USER_SETTINGS',
                             'User-defined settings are expected in module %s' % USER_SETTINGS_PATH,
                             'User-defined settings found in module %s' % USER_SETTINGS_PATH, ))


__settings = globals()
__formatter = string.Formatter()
__settings_origin = {}


def __parse_setting(obj):
    if isinstance(obj, str):
        values = {'PROJECT_NAME': PROJECT_NAME}
        for (literal_text, field_name, format_spec, conversion) in __formatter.parse(obj):
            if field_name is not None:
                values[field_name] = __setting_value(field_name)
        if values:
            return __formatter.format(obj, **values)
    elif isinstance(obj, DirectoryPath):
        obj = __parse_setting(str(obj))
        __ensure_dir(obj, parent_=False)
        return obj
    elif isinstance(obj, FilePath):
        obj = __parse_setting(str(obj))
        __ensure_dir(obj, parent_=True)
        return obj
    elif isinstance(obj, Path):
        return __parse_setting(str(obj))
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [__parse_setting(x) for x in obj]
    elif isinstance(obj, dict):
        return dict([(__parse_setting(x), __parse_setting(y)) for (x, y) in obj.items()])
    return obj


def __setting_value(setting_name_):
    """ import setting_name_ from user-specific settings, or project-specific settings, or django-floor settings.
    Also add it to globals(), so this function is idempotent.

    :param setting_name_: name of the setting to import
    :return: the imported setting :)
    """
    if setting_name_ in __settings:
        return __settings[setting_name_]
    if hasattr(user_settings, setting_name_):
        value = getattr(user_settings, setting_name_)
        __settings_origin[setting_name_] = 'user'
    elif hasattr(project_settings, setting_name_):
        value = getattr(project_settings, setting_name_)
        __settings_origin[setting_name_] = 'project'
    else:
        value = getattr(floor_settings, setting_name_)
        __settings_origin[setting_name_] = 'default'
    __settings[setting_name_] = __parse_setting(value)
    return __settings[setting_name_]


def __ensure_dir(path_, parent_=True):
    dirname_ = os.path.dirname(path_) if parent_ else path_
    if not os.path.isdir(dirname_):
        try:
            os.makedirs(dirname_)
            print('Directory %s created.' % dirname_)
        except IOError:
            print('Unable to create directory %s.' % dirname_)

for module in floor_settings, project_settings, user_settings:
    for setting_name in module.__dict__:
        if setting_name == setting_name.upper():
            __setting_value(setting_name)


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable
INSTALLED_APPS += list(filter(lambda x: x not in INSTALLED_APPS, OTHER_ALLAUTH))
# noinspection PyUnresolvedReferences
INSTALLED_APPS += list(filter(lambda x: x not in INSTALLED_APPS, FLOOR_INSTALLED_APPS))


if __name__ == '__main__':
    import doctest

    doctest.testmod()