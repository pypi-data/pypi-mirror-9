import datetime
import os

import click
import yaml

from .build import Build
from .config import Configuration


def create_post(config, post_name):
    'Create the directories for today and dump the named file down there.'
    post_filename = "{0}.rst".format(post_name)
    path = os.path.join(config.blogroot,
                        datetime.datetime.now().strftime('%Y/%m/%d'))
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    post_filepath = os.path.join(path, post_filename)
    with open(post_filepath, 'a'):
            os.utime(post_filepath, None)
    click.echo(post_filepath)


@click.command()
@click.argument('config_path', type=click.Path(), default='bade.yaml')
@click.option('--debug', is_flag=True, help='Print debugging info')
@click.option('--force', is_flag=True, help='Force a complete build.')
@click.option('--post', help='Create a blog post for today.')
def main(config_path, debug, force, post):
    'Command line interface for bade'
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config_dict = yaml.load(config_file.read())
            config = Configuration(config_dict, {'debug': debug})
    else:
        config = Configuration({})
    if post:
        create_post(config, post)
        exit()
    build = Build(config)
    if force:
        build.clean()
        # other stuff
    build.run()
