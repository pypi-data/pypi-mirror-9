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
              expose_value=False, is_eager=True)
def main():
    """
    Welecome to EManual!
    """
    pass


@main.command()
def create():
    """
    Create the info.json File
    """
    make.create_info()


@main.command()
@click.option('--port', default=8000, help='port to listen')
def server(port):
    """
    Server to preview the markdown files
    """
    import os
    os.system('python -m SimpleHTTPServer %s' % port)
