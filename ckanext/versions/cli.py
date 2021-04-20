# encoding: utf-8
import logging

import click
from ckan.model import Package, Resource, Session
from ckan.plugins import toolkit

from ckanext.versions.logic import action
from ckanext.versions.model import Version, create_tables, tables_exist


def _log():
    return logging.getLogger(__name__)


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
        ctx.exit(1)

    create_tables()
    click.secho('Dataset versions tables created', fg="green")


@versions.command()
@click.pass_context
def cleandb(ctx):
    """Creates the necessary tables in the database.
    """
    if tables_exist():
        click.secho('Dataset versions tables already exist', fg="green")
        ctx.exit(1)

    create_tables()
    click.secho('Dataset versions tables created', fg="green")


@versions.command()
@click.pass_context
@click.option('--name', default='1.0')
@click.option('--notes', default='Initial version.')
def create_initial_version(ctx, name, notes):
    """Creates an initial resource version for all existing resources.

    The creator of the version will be set as the package creator.
    """
    resources = _get_list_of_resources_without_version()

    if not resources:
        click.secho('All resources contains at least one version.', fg="green")
        ctx.exit(1)

    click.secho(
        "Creating initial version for {} resources.".format(len(resources))
        )
    for resource in resources:
        _create_resource_initial_version(resource, name, notes)
    click.secho("Initial versions created succesfully.")


def _get_list_of_resources_without_version():
    session = Session()
    resources = session.query(Resource.id, Package.creator_user_id).\
        filter(Resource.state != 'deleted').\
        join(Package).\
        order_by(Resource.created).\
        all()

    if not resources:
        return None

    versions = session.query(Version.resource_id).distinct()

    resources_with_version = [v.resource_id for v in versions]

    result = [r for r in resources if r.id not in resources_with_version]

    return result


def _create_resource_initial_version(resource, name, notes):
    context = {'ignore_auth': True}
    data_dict = {
        'resource_id': resource.id,
        'name': name,
        'notes': notes,
        'creator_user_id': resource.creator_user_id
    }
    try:
        action.resource_version_create(context, data_dict)
    except toolkit.ObjectNotFound:
        _log().debug("Resource %s not found.", resource.id)


def get_commands():
    return [versions]
