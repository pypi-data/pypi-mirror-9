# -*- coding: utf-8 -*-
import os
import click
import ConfigParser

APP_NAME = 'rackcli'


def validate_path(value):
    if not value:
        return False
    elif not os.path.isfile(value):
        click.echo('configuration option invalid, %s is not a file.' % value)
        return False
    return value


def load_config(debug, override):
    """ Pulls the rackcli configuration file and reads it if it exists
    otherwise, warn the user.
    """
    if debug:
        click.echo('Attempting to load raxcli config.ini file.')
    if override:
        validate_path(override)
    # todo: handle windows %user stuff
    config_home = os.environ.get('RX_CONFIG_HOME') or \
        os.path.expanduser('~/.config')
    if not override:
        possible_configs = [os.path.join(config_home, "rackcli", "config.ini"),
                            os.path.join(os.path.expanduser("~/.rackcli"),
                            "config.ini"),
                            os.path.join(".rackcli", "config.ini")]
    else:
        possible_configs = [override]
    parser = ConfigParser.RawConfigParser()
    for cfg in possible_configs:
        if os.path.isfile(cfg):
            parser.read([cfg])
        rv = {}
        for section in parser.sections():
            sect = {}
            for key, value in parser.items(section):
                sect[key] = value
            rv[section] = sect
        if not rv and debug:
            click.echo("Warning: could not load %s." % cfg)
    return rv
