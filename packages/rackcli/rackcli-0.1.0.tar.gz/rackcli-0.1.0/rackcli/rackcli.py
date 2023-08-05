# -*- coding: utf-8 -*-

"""
rackcli.py

Apache License 2.0

Stuff
"""
import click
import config


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    # how do I get this from __init__.py fml
    click.echo('0.1.0-alpha')
    ctx.exit()


@click.command()
@click.option('--debug', '-d', is_flag=True, default=False)
@click.option('--no-verify-ssl', is_flag=True, default=False,
              help='Disable SSL - not recommended, considered harmful')
@click.option('--config-file', '-c', required=False,
              help='Optional Configuration file to use')
@click.option('--output', '-o', required=False, default='table',
              type=click.Choice(['json', 'text', 'table']),
              help='The formatting style for command output.')
@click.option('--profile', '-p', required=False,
              help='Use a specific profile from your credential file.')
@click.option('--region', '-r', required=False,
              help='The region to use. Overrides config/env settings.')
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
def cli(debug, no_verify_ssl, config_file, output, profile, region):
    """ rackcli [options] <command> <subcommand> [parameters] """
    overrides = False
    if config_file:
        overrides = config.validate_path(config_file)
    # dump the loaded config - throwaway
    click.echo(config.load_config(debug, overrides))
    click.echo('Hello World')
