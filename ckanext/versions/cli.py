# encoding: utf-8

import click

from ckanext.versions.model import create_tables, tables_exist


@click.group()
def versions():
    '''versions commands
    '''
    pass


@versions.command()
@click.pass_context
def initdb(ctx):
    """Creates the necessary tables in the database.
    """
    if tables_exist():
        click.secho('Dataset versions tables already exist', fg="green")
        ctx.exit(0)

    create_tables()
    click.secho('Dataset versions tables created', fg="green")


@versions.command()
@click.pass_context
def cleandb(ctx):
    """Creates the necessary tables in the database.
    """
    if tables_exist():
        click.secho('Dataset versions tables already exist', fg="green")
        ctx.exit(0)

    create_tables()
    click.secho('Dataset versions tables created', fg="green")


def get_commands():
    return [versions]
