#!/usr/bin/python
# -*- coding: utf-8 -*-
import click
import os


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def unique_profile(ctx, param, value):
    if value in ctx.obj['profiles']:
        raise click.BadParameter('Profile \'%s\' does already exist' % value)

    return value


def existing_profile(ctx, param, value):
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


@click.group()
@click.option('--global-profiles/--local-profiles', '-g/-l',
              default=True,
              help='Use the global profiles from the home folder or'
              + 'a local set of profiles from the current folder.')
@click.pass_context
def cli(ctx, global_profiles):
    """ Manages the profiles for the aiqpy library """
    import json
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
            import json
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
    import codecs
    password_encoder = codecs.getencoder("rot-13")

    ctx.obj['profiles'][profile_name] = {
        'username': username,
        'password': password_encoder(password)[0],
        'platform': platform_url,
        'organization': organization,
        'scope': scope
    }

    if click.confirm('Do you want to test the account?', default=True):
        import aiqpy
        connection = aiqpy.Connection(username, password, organization,
                                      platform_url, scope=scope)
        try:
            say('Connecting to %s...' % platform_url)
            connection.login()
            connection.logout()
        except aiqpy.exceptions.AIQPYException as exception:
            say(exception.message, 'fail')
            click.confirm('Do you want to create the profile anyway?',
                          abort=True)

        else:
            say('Login successful!', 'success')

    ctx.obj['updated'] = True


@cli.command()
@click.pass_context
def list(ctx):
    """ Lists the avaliable profiles """
    for name, profile in ctx.obj['profiles'].iteritems():
        click.echo('Profile: %s' % name)
        for parameter, value in profile.iteritems():
            if parameter == 'password':
                continue
            click.echo('\t %s: %s' % (parameter.capitalize(), value))


@cli.command()
@click.argument('profile-name', callback=existing_profile)
@click.pass_context
def edit(ctx, profile_name):
    " Edits an existing profile "
    import json
    pretty_json = json.dumps(ctx.obj['profiles'][profile_name], indent=4)
    updated_profile = click.edit(pretty_json)

    try:
        profile_json = json.loads(updated_profile)
    except ValueError:
        say('Invalid JSON', 'fail')
    else:
        if not profile_json == ctx.obj['profiles'][profile_name]:
            ctx.obj['profiles'][profile_name] = profile_json
            ctx.obj['updated'] = True


def main():
    cli(obj={'updated': False})

if __name__ == '__main__':
    main()
