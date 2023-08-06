#!/usr/bin/env python
#
# Copyright 2015 Valentine Gogichashvili
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""pydidit script to update idonethis topics

.. moduleauthor:: Valentine Gogichashvili <valgog@gmail.com>

"""

from __future__ import print_function, unicode_literals
import os
from textwrap import dedent
import click
import requests

ENV_DIDIT_TEAM = 'DIDIT_TEAM'
ENV_DIDIT_API_TOKEN = 'DIDIT_API_TOKEN'

class Config:
    """Config object represents the current configuration"""
    def __init__(self):
        # TODO: load all the needed envvars here and throw exception if they are not defined
        self.url = 'https://idonethis.com/api/v0.1'
        self.team = os.environ.get(ENV_DIDIT_TEAM)
        self.api_token = os.environ.get(ENV_DIDIT_API_TOKEN)


pass_config = click.make_pass_decorator(Config, ensure=True)


def get_message_from_editor():
    marker = dedent('''
        #
        # Enter the thing you just did.
        #
        # You can use '#' to hash some topics.
        #
        # Prefix your text with [] to send a goal.
        #
        ''')
    message = click.edit('\n\n' + marker)
    if message is not None:
        return message.split(marker, 1)[0].rstrip('\n')


def send(config, done):
    """Send your progress to idonethis.com"""
    if done:
        message = ' '.join(done).strip()
    else:
        message = get_message_from_editor()
    message = message.strip() if message is not None else None
    if message:
        click.echo("Sending to team ", nl=False)
        click.secho(config.team, nl=False, bold=True)
        click.echo(' ', nl=False)
        click.secho(message, fg='green')
        r = requests.post(
            config.url + '/dones/',
            json={'raw_text': message,
                  'team': config.team,
                  },
            headers={'Authorization': 'Token ' + config.api_token}
        )
        if r.status_code == requests.codes.created:
            click.secho('Done')
        else:
            click.secho('Could not post data {} {}'.format(r.status_code, r.text))


def get_user_teams(config):
    r = requests.get(config.url + '/teams', headers={'Authorization': 'Token ' + config.api_token})
    if r.status_code == requests.codes.ok:
        result = r.json()
        # click.echo(result)
        teams = result['results']
        if teams:
            return [ team['short_name'] for team in teams ]
        else:
            return []

def get_user_for_api_token(config):
    r = requests.get(config.url + '/noop', headers={'Authorization': 'Token ' + config.api_token})
    if r.status_code == requests.codes.ok:
        result = r.json()
        return result['user']
    else:
        return None


HINT_API_TOKEN = '--api-token or {} environment variable'.format(ENV_DIDIT_API_TOKEN)
HINT_TEAM = '--team or {} environment variable'.format(ENV_DIDIT_TEAM)

@click.command()
@click.option('--team', type=str, help='team to post the status update for (can be defined by {} environment varable)'.format(ENV_DIDIT_TEAM))
@click.option('--api-token', type=str, help='API token (can be defined by {} environment varable)'.format(ENV_DIDIT_API_TOKEN))
@click.option('--test-api-token', is_flag=True, help='test if the proved API token works')
@click.argument('done', nargs=-1)
@pass_config
def cli(config, team, api_token, test_api_token, done):
    config.team = team or config.team
    config.api_token = api_token or config.api_token
    if not config.api_token:
        raise click.BadParameter('api token should be defined', param_hint=HINT_API_TOKEN)
    if test_api_token:
        user = get_user_for_api_token(config)
        if user:
            click.echo('Connected as user ', nl=False)
            click.secho(user, fg='green')
            click.echo('API token is ok')
            teams = get_user_teams(config)
            click.echo('Member of {}'.format(', '.join(teams)))
            if config.team:
                if config.team not in teams:
                    click.echo('Configured team ', nl=False)
                    click.secho(config.team, fg='green', nl=False)
                    click.echo(' does not match available teams for user ', nl=False)
                    click.secho(user, fg='green')
            elif len(teams) != 1:
                click.secho('team should be configired by {}'.format(HINT_TEAM), fg='red')
            raise SystemExit()
        else:
            raise click.BadParameter('could not connect using provided api token', param_hint=HINT_API_TOKEN)
    if not config.team:
        teams = get_user_teams(config)
        if teams:
            if len(teams) == 1:
                config.team = iter(teams).next()
            else:
                raise click.ClickException('user is a member of more then one team ({}). team should be configured using {}!'.format(', '.join(teams), HINT_API_TOKEN))
        else:
            raise click.ClickException('team should be defined')
    send(config, done)


if __name__ == '__main__':
    cli()

