#!/usr/bin/env python

import arrow
import click
from requests_oauthlib import OAuth2Session

AUTH_URL = 'https://my.freshbooks.com/service/auth/oauth/authorize'
TOKEN_URL = 'https://api.freshbooks.com/auth/oauth/token'
HEADERS = {
    'Api-Version': 'alpha',
    'User-Agent': 'FreshBooks API (python) 1.0.0',
    'Content-Type': 'application/json'
}


@click.command()
@click.argument('client-id')
@click.argument('client-secret')
@click.argument('redirect-url')
def cli(client_id, client_secret, redirect_url):
    """
    Do the OAuth dance with FreshBooks API server to get the access token.
    """
    auth_url, state = get_auth_info(client_id, redirect_url)
    display_auth_info(auth_url)
    response = click.prompt('Paste the response URL')
    token = get_access_token(
        client_id, client_secret, redirect_url, state, response
    )
    display_token(token)


def get_auth_info(client_id, redirect_url):
    oauth = OAuth2Session(client_id, redirect_uri=redirect_url)
    auth_url, state = oauth.authorization_url(AUTH_URL)
    return auth_url, state


def get_access_token(client_id, client_secret, redirect_url, state, response):
    freshbooks = OAuth2Session(
        client_id, token=state, redirect_uri=redirect_url
    )
    freshbooks.headers.update(HEADERS)
    token = freshbooks.fetch_token(
        TOKEN_URL, client_secret=client_secret, authorization_response=response
    )
    return token


def display_auth_info(auth_url):
    click.echo('Visit the following URL to authorize access to FreshBooks:')
    click.echo(auth_url)
    click.echo(
        'You will most likely be redirected to a non-existent page, '
        'which is OK. Be sure to copy the URL that you’re redirected to, '
        'we’ll need it for the next step.'
    )


def display_token(token):
    expiration = arrow.get(token['expires_at'])
    click.echo(f"Access token: {token['access_token']}")
    click.echo(
        f"Expires {expiration.humanize()} "
        f"at {expiration.to('local').isoformat()}"
    )


if __name__ == '__main__':
    cli()
