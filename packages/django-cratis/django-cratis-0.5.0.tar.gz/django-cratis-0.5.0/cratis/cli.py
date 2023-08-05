import os
import sys
import yaml
import string
import random


def read_yaml_file(_file):
    with open(_file) as f:
        return yaml.load(f)


def _find_project_env(path):
    """
    Finds cratis.yml for cratis command.

    Algorithm is following:

    * Check current directory
    * If no cratis.yml, check parent and reapeat until found

        * Nothing found, return None
        * If found, check if parent also contains cratis.yml

            * If parent contains, then return parent's cratis.yml path
            * If no, then return current dir cratis.yml

    """
    env_file_name = '%s/cratis.yml' % path
    env_parent_file_name = '%s/cratis.yml' % os.path.dirname(path)

    if os.path.exists(env_file_name):
        if os.path.exists(env_parent_file_name):
            return env_parent_file_name
        return env_file_name
    elif path != '/':
        return _find_project_env(os.path.dirname(path))
    else:
        return None


class NotProperlyConfigured(Exception):
    pass


class NoVariableDefined(NotProperlyConfigured):
    def __init__(self, var_name, *args, **kwargs):
        super(NoVariableDefined, self).__init__(*args, **kwargs)
        self.var_name = var_name


class NoConfigFile(NotProperlyConfigured):
    pass


class NoCratisApp(NotProperlyConfigured):
    pass


def load_env():

    """
    Loads environment variables defined in cratis.yml file.

    load_env() finds cratis.yml file in current directory, then in it's parent and
    so on until it finds, or root dir reached ("/").
    If no cratis.yml found, then error shown.

    Some variables are required for cratis to work::

    - CRATIS_APP_PATH - Path where cratis application is located. (default ".")
    - DJANGO_SETTINGS_MODULE - Where to find settings module (Default "settings", means settings.py file in CRATIS_APP_PATH)
    - DJANGO_CONFIGURATION - One of Environments defined in settings.py (default "Dev")

    *Dev mode*

    In development mode all valuesare meant to be used with default values, and cratis.yml
    is just a marker of where your project is located. Very useful when you execute cratis
    command from subdirectory of your project (yes, you can do this!).

    Structure in this case will be following::

        - myproject/
          - .git
          - settings.py
          - cratis.yml

    *Production mode*

    In production mode, cratis.yml plays important role of providing environment information.

    Structure in this case will be following::

        - myproject/
          - src/
            - .git
            - settings.py
            - cratis.yml
          - cratis.yml

    Note: cratis.yml that is located one level up will always get priority.

    cratis.yml file contents::

        CRATIS_APP_PATH': myproject,
        DJANGO_CONFIGURATION': Prod,
        DJANGO_SETTINGS_MODULE: settings

        SOME_OTHER_ENV_VARIABLE: xxx
        ...

    Django-Configurations highly relays on ENV variables, so you can easily redefine some settings
    through Env variables.

    """
    _file = _find_project_env(os.getcwd())
    if not _file:
        raise NotProperlyConfigured('Can not find cratis.yml in current directory or any of parents.')
    else:
        for key, val in read_yaml_file(_file).iteritems():
            val = str(val)
            if not key in os.environ:
                os.environ[key] = val

    if not "CRATIS_APP_PATH" in os.environ:
        raise NoVariableDefined("CRATIS_APP_PATH", 'Found cratis.yml, but it do not contain CRATIS_APP_PATH. Corrupted file?')

    if not "DJANGO_CONFIGURATION" in os.environ:
        raise NoVariableDefined("DJANGO_CONFIGURATION", 'Found cratis.yml, but it do not contain DJANGO_CONFIGURATION. Corrupted file?')

    if not "DJANGO_SETTINGS_MODULE" in os.environ:
        raise NoVariableDefined("DJANGO_SETTINGS_MODULE", 'Found cratis.yml, but it do not contain DJANGO_SETTINGS_MODULE. Corrupted file?')

    if not os.path.exists(os.environ["CRATIS_APP_PATH"]):
        raise NoCratisApp('Path specified in CRATIS_APP_PATH do not exist: %s' % os.environ["CRATIS_APP_PATH"])

    sys.path += (os.environ["CRATIS_APP_PATH"], )


def cratis_cmd():
    """
    Command that executes django ./manage.py task + loads environment variables from cratis.yml

    Command also can be executed from sub-folders of project.
    """

    try:
        load_env()

        from configurations.management import execute_from_command_line

        execute_from_command_line(sys.argv)

    except NotProperlyConfigured as e:
        print('\n\tError: %s\n' % e.message)





class AlreadyExistsException(Exception):
    pass


def cratis_init_cmd():
    """
    Command creates new cratis project in current directory.
    Two files are generated:

    * Empty settings file
    * cratis.yml configured to serve project from current directory.

    Usage::

      cratis-init
      cratis runserver

    """
    path = os.path.join(os.getcwd(), 'cratis.yml')
    path_settings = os.path.join(os.getcwd(), 'settings.py')

    if os.path.exists(path):
        raise AlreadyExistsException('File cratis.yml already exist in current directory.')
    else:
        with open(path, 'w+') as f:
            yaml.dump({
                'CRATIS_APP_PATH': '.',
                'DJANGO_CONFIGURATION': 'Dev',
                'DJANGO_SETTINGS_MODULE': 'settings'
            }, f, default_flow_style=False)

    if os.path.exists(path_settings):
        raise AlreadyExistsException('File settings.py already exist in current directory.')
    else:
        with open(path_settings, 'w+') as f:
            f.write('''# coding=utf-8
from cratis.settings import CratisConfig


class Dev(CratisConfig):
    DEBUG = True
    SECRET_KEY = '%s'

    FEATURES = (
        # your features here
    )


class Test(Dev):
    pass


class Prod(Dev):
    DEBUG = False

    FEATURES = Dev.FEATURES + (
        # your features here
    )
''' %  ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(30)]))