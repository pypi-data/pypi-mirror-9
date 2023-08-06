""" Load and parse configuration file
"""
import ConfigParser
import os
import yaml

def load_config(config_file=None):
    """Loads a configuration file.

    By default it assumes ~/.taca/taca.conf
    """
    try:
        if not config_file:
            config_file = os.path.join(os.environ.get('HOME'), '.taca', 'taca.conf')
        config = ConfigParser.SafeConfigParser()
        with open(config_file) as f:
            config.readfp(f)
        return config
    except IOError:
        raise IOError(("There was a problem loading the configuration file. "
                "Please make sure that ~/.taca/taca.conf exists and that you have "
                "read permissions"))


def load_yaml_config(config_file):
    """Load YAML config file

    :param str config_file: The path to the configuration file.

    :returns: A dict of the parsed config file.
    :rtype: dict
    :raises IOError: If the config file cannot be opened.
    """
    if type(config_file) is file:
        return yaml.load(config_file)
    else:
        try:
            with open(config_file, 'r') as f:
                return yaml.load(f)
        except IOError as e:
            e.message = "Could not open configuration file \"{}\".".format(config_file)
            raise e
