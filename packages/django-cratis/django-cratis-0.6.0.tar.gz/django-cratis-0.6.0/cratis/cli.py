import os
import sys


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
    env_file_name = '%s/settings.py' % path
    env_parent_file_name = '%s/settings.py' % os.path.dirname(path)

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
    _file = _find_project_env(os.getcwd())
    if not _file:
        raise NotProperlyConfigured('Can not find settings.py in current directory or any of parents.')
    else:
        for key, val in {
            'CRATIS_APP_PATH': '.',
            'DJANGO_CONFIGURATION': 'Dev',
            'DJANGO_SETTINGS_MODULE': 'settings',
        }.iteritems():
            val = str(val)
            if not key in os.environ:
                os.environ[key] = val

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

