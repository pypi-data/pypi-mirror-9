import ConfigParser
import os

def get_config(config_name, env_name=None):
    """Load a config file.

    We look in various locations for a config file, starting with the
    default one in the app's current directory. We then check the user's
    home directory before looking for the appropriate environment variable.
    """
    if not env_name:
        env_name = '%s_CONF' % config_name.split('.')[0]

    config = ConfigParser.RawConfigParser()

    path_to_config = os.path.join(os.path.dirname(__file__), config_name)

    home_path = os.path.expanduser('~/.%s' % config_name)
    paths = [path_to_config, home_path, ]

    if env_name in os.environ:
        paths.append(os.environ[env_name])

    config.read(paths)

    return config

settings = get_config(config_name='filewatch.ini')