#!/usr/bin/env python

import json
import os
import sys
from pathlib import Path

import arrow
import click

APP_ROOT = Path(__file__).parents[1].resolve()
sys.path.append(str(APP_ROOT))

from freshbooks.api import Client  # noqa isort:skip


@click.command()
@click.argument('access-token')
@click.argument('business-name')
@click.argument('client-name')
@click.argument('project-name')
@click.argument('service-name')
def cli(access_token, business_name, client_name, project_name, service_name):
    """
    Create a test time entry, then delete it.
    """
    fb = Client(access_token)
    account_id, business_id = fetch_business_info(fb, business_name)
    client_id = fetch_client_id(fb, account_id, client_name)
    project_id, service_id = fetch_project_and_service_ids(
        fb, business_id, client_id, project_name, service_name
    )

    started_at = arrow.now().format('YYYY-MM-DDTHH:mm:ss.SSS') + 'Z'
    duration = 30 * 60
    note = 'This is a test…'
    time_entry = create_time_entry(
        fb, business_id, client_id, project_id, service_id, started_at,
        duration, note
    )
    click.echo(f"Response: {json.dumps(time_entry, indent=2)}")
    click.echo(
        'Verify time entry at https://my.freshbooks.com/#/time-tracking/'
    )


def fetch_business_info(api_client, business_name):
    my_info = api_client.business_roles_identity
    memberships = my_info['business_memberships']
    business = next(
        m['business'] for m in memberships
        if m['business']['name'] == business_name
    )
    return business['account_id'], business['id']


def fetch_client_id(api_client, account_id, client_name):
    filter = {'organization_like': client_name}
    clients = api_client.list_clients(account_id, filter)['clients']
    client = _handle_edge_cases(clients, 'organization', 'client', client_name)
    return client['id']


def fetch_project_and_service_ids(
        api_client, business_id, client_id, project_name, service_name
):
    filter = {'complete': False}
    all_projects = api_client.list_projects(business_id, filter)['projects']
    projects = [
        p for p in all_projects
        if p['client_id'] == client_id
        and p['title'] == project_name
    ]
    project = _handle_edge_cases(projects, 'id', 'project', project_name)
    service_id = fetch_service_id(project, service_name)

    return project['id'], service_id


def fetch_service_id(project, service_name):
    services = [s for s in project['services'] if s['name'] == service_name]
    _handle_no_results(services, 'service', service_name)
    return services[0]['id']


def create_time_entry(
        api_client, business_id, client_id, project_id, service_id, started_at,
        duration, note, is_logged=True
):
    entry_info = dict(
        client_id=client_id,
        project_id=project_id,
        service_id=service_id,
        started_at=started_at,
        duration=duration,
        note=note,
        is_logged=is_logged
    )
    entry = api_client.create_time_entry(business_id, entry_info)
    return entry


def _handle_edge_cases(obj_list: list, obj_key: str, label: str, value: str):
    _handle_no_results(obj_list, label, value)

    choice = 0
    if len(obj_list) > 1:
        message = f'''
There were {len(obj_list)} "{value}" {label}s, pick one:

'''
        for i, obj in enumerate(obj_list, start=1):
            message += f"{i}. {obj[obj_key]}{os.linesep}"

        choice = click.prompt(message, type=int) - 1

    result = obj_list[choice]
    return result


def _handle_no_results(obj_list, label, value):
    ctx = click.get_current_context()
    if len(obj_list) is 0:
        ctx.fail(f'Could not find {label} "{value}"')


if __name__ == '__main__':
    cli()
