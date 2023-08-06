# -*- coding: utf-8 -*-
"""Help managing the aiqpy profile"""
import click
import codecs
import json
import os
import six
from aiqpy.connection import Connection
from aiqpy.exceptions import AIQPYException


def abort_if_false(ctx, _, value):
    if not value:
        ctx.abort()


def unique_profile(ctx, _, value):
    if value in ctx.obj['profiles']:
        raise click.BadParameter('Profile \'%s\' does already exist' % value)

    return value


def existing_profile(ctx, _, value):
    if value not in ctx.obj['profiles']:
        raise click.BadParameter('Profile \'%s\' does not exist' % value)

    return value


def say(message, status='info'):
    colormap = {
        'info': 'yellow',
        'success': 'green',
        'fail': 'red'
    }

    fg_color = colormap.get(status, 'yellow')
    click.secho(status.upper() + ':', bg=fg_color, nl=False)
    click.echo(' ' + message)


def encode_password(unencoded_password):
    password_encoder = codecs.getencoder("rot-13")
    return password_encoder(unencoded_password)[0]


def test_profile(profile_data):
    profile_data['password'] = encode_password(profile_data['password'])
    connection = Connection(**profile_data)
    try:
        say('Connecting to %s...' % connection.platform_url)
        connection.login()
        connection.logout()
        return True
    except AIQPYException as exception:
        say(exception.message, 'fail')
        return False


@click.group()
@click.option('--global-profiles/--local-profiles', '-g/-l',
              default=True,
              help='Use the global profiles from the home folder or'
              + 'a local set of profiles from the current folder.')
@click.pass_context
def cli(ctx, global_profiles):
    """ Manages the profiles for the aiqpy library """
    if global_profiles:
        profiles_path = os.path.expanduser('~/.aiqpy_profiles')
    else:
        profiles_path = os.path.join(os.getcwd(), '.aiqpy_profiles')

    ctx.obj['profiles_path'] = profiles_path

    if os.path.isfile(profiles_path) > 0:
        with open(profiles_path, 'r') as profiles_file:
            profiles = json.load(profiles_file)
            ctx.obj['profiles'] = profiles
    else:
        ctx.obj['profiles'] = {}


@cli.resultcallback()
@click.pass_context
def the_end(ctx, *args, **kwargs):
    if ctx.obj['updated']:
        with open(ctx.obj['profiles_path'], 'w') as profiles_file:
            json.dump(ctx.obj['profiles'], profiles_file)

        say('Profiles updated!', 'success')


@cli.command()
@click.argument('profile-name', callback=existing_profile)
@click.option('--yes', '-y',
              is_flag=True,
              callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to remove the profile?',
              help='Proceed to remove the profile without manual confirmation')
@click.pass_context
def remove(ctx, profile_name):
    """ Removes the specified profile """
    del ctx.obj['profiles'][profile_name]
    ctx.obj['updated'] = True


@cli.command()
@click.argument('profile-name', callback=unique_profile)
@click.option('--username',
              prompt=True,
              help='The username for the new profile')
@click.password_option(help='The password for the new profile')
@click.option('--organization',
              prompt=True,
              help='The organization for the new profile')
@click.option('--platform-url',
              prompt=True,
              help='The platform URL to connect to for the new profile')
@click.option('--scope',
              prompt=True,
              default='admin',
              help='The scope(s) to use while logging in as a space'
              + ' separated list. Example: "device admin". Default: admin')
@click.pass_context
def add(ctx,
        profile_name,
        username,
        password,
        organization,
        platform_url,
        scope):
    """ Adds a new profile """

    ctx.obj['profiles'][profile_name] = {
        'username': username,
        'password': encode_password(password),
        'platform': platform_url,
        'organization': organization,
        'scope': scope
    }

    if 'integration' in scope:
        solution = click.prompt('Solution name', default=organization)
        ctx.obj['profiles'][profile_name]['auth_params'] = {
            'x-solution': solution
        }

    if click.confirm('Do you want to test the account?', default=True):
        if not test_profile(ctx.obj['profiles'][profile_name]):
            click.confirm('Do you want to create the profile anyway?',
                          abort=True)

        else:
            say('Login successful!', 'success')

    ctx.obj['updated'] = True


@cli.command()
@click.pass_context
def list(ctx):
    """ Lists the avaliable profiles """
    for name, profile in six.iteritems(ctx.obj['profiles']):
        click.echo('Profile: %s' % name)
        for parameter, value in six.iteritems(profile):
            if parameter == 'password':
                continue
            click.echo('\t %s: %s' % (parameter.capitalize(), value))


@cli.command()
@click.argument('profile-name', callback=existing_profile)
@click.pass_context
def edit(ctx, profile_name):
    """ Edits an existing profile """

    profile = ctx.obj['profiles'][profile_name]
    profile['password'] = encode_password(profile['password'])
    pretty_json = json.dumps(profile, indent=4)
    updated_profile = click.edit(pretty_json)

    if not updated_profile:
        ctx.abort()

    try:
        profile_json = json.loads(updated_profile)
    except ValueError:
        say('Invalid JSON', 'fail')
    else:
        if profile_json == ctx.obj['profiles'][profile_name]:
            ctx.abort()
        else:
            ctx.obj['updated'] = True

        profile_json['password'] = encode_password(profile_json['password'])

        ctx.obj['profiles'][profile_name] = profile_json

        if click.confirm('Do you want to test the account?', default=True):
            if not test_profile(profile_json):
                click.confirm("Do you want to update the profile anyway?",
                              abort=True)
            else:
                say('Login successful!', 'success')


@cli.command()
@click.argument('profile-name', required=False)
@click.pass_context
def login(ctx, profile_name):
    """ Logs in to the platform """
    if profile_name:
        profile = ctx.obj['profiles'][profile_name]
        profile['password'] = encode_password(profile['password'])
    else:
        profile = {
            'username': click.prompt('Username'),
            'password': click.prompt('Password', hide_input=True),
            'organization': click.prompt('Organization'),
            'platform': click.prompt('Platform URL'),
            'scope': click.prompt('Scope', default='admin',
                                  type=click.Choice([
                                      'admin',
                                      'integration',
                                      'device'
                                  ]))
        }

        if 'integration' in profile['scope']:
            profile['auth_params'] = {
                'x-solution': click.prompt('Solution',
                                           default=profile['organization'])
            }

    test_connection = Connection(**profile)
    try:
        test_connection.login()
    except AIQPYException as exception:
        say(exception.message, 'fail')
    else:
        say('Login successful', 'success')
        say('Access token: %s' % test_connection.access_token, 'info')


def main():
    cli(obj={'updated': False})

if __name__ == '__main__':
    main()
