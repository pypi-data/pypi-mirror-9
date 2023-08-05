# -*- coding: utf-8 -*-


from emanual import make, __version__
import click


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Show the version')
def main():
    """
    Welecome to EManual CLI!
    """
    pass


@main.command('create')
@click.argument('lang',)
def create_info(lang):
    """
    Create the info.json File for Given Lang 
    """
    make.create_info(lang)


@main.command('server')
@click.option('--port', default=8000, help='port to listen')
def server(port):
    """
    Server to preview the markdown files
    """
    import os
    os.system('python -m SimpleHTTPServer %s' % port)


@main.command('dist')
@click.argument('lang', )
def dist(lang):
    """
    Distributing the markdown
    """
    make.dist_zip(lang)
