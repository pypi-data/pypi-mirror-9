#!/usr/bin/env python3
'''
Helper script to request access to a certain host.
'''

import click
import json
import keyring
import os
import requests
import yaml


KEYRING_KEY = 'piu'

CONFIG_DIR_PATH = click.get_app_dir('piu')
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'piu.yaml')

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('host', metavar='[USER]@HOST')
@click.argument('reason')
@click.argument('reason_cont', nargs=-1, metavar='[..]')
@click.option('-u', '--user', help='Username to use for authentication', envvar='USER')
@click.option('-p', '--password', help='Password to use for authentication', envvar='SSH_REQUEST_PASSWORD')
@click.option('-r', '--remote-host', help='Remote host name (use "host" as bastion host)')
@click.option('--url', help='SSH Access Granting Service URL', envvar='SSH_ACCESS_GRANTING_SERVICE_URL')
@click.option('--insecure', help='Do not verify SSL certificate', is_flag=True, default=False)
def cli(host, user, password, remote_host, reason, reason_cont, url, insecure):
    # sdf
    parts = host.split('@')
    if len(parts) > 1:
        username = parts[0]
    else:
        username = user

    hostname = parts[-1]

    reason = ' '.join([reason] + list(reason_cont)).strip()

    cacert = not insecure

    if not url:
        if not os.path.exists(CONFIG_FILE_PATH):
            os.makedirs(CONFIG_DIR_PATH, exist_ok=True)
            url = click.prompt('Please enter the SSH Access Granting Service URL')
            config = {'url': url}
            with open(CONFIG_FILE_PATH, 'w') as fd:
                yaml.dump(config, fd)

        with open(CONFIG_FILE_PATH, 'rb') as fd:
            config = yaml.safe_load(fd)
        url = config['url']
        if 'cacert' in config:
            cacert = config['cacert']

    password = password or keyring.get_password(KEYRING_KEY, user)

    if not password:
        password = click.prompt('Password', hide_input=True)

    if not url.endswith('/access-requests'):
        url = url.rstrip('/') + '/access-requests'
    data = {'username': username, 'hostname': hostname, 'reason': reason}
    if remote_host:
        data['remote-host'] = remote_host
    click.secho('Requesting access to host {hostname} for {username}..'.format(**vars()), bold=True)
    r = requests.post(url, headers={'Content-Type': 'application/json'},
                      data=json.dumps(data), auth=(user, password),
                      verify=cacert)
    if r.status_code == 200:
        click.secho(r.text, fg='green', bold=True)
        ssh_command = ''
        if remote_host:
            ssh_command = 'ssh {username}@{remote_host}'.format(**vars())
        click.secho('You can now access your server with the following command:')
        click.secho('ssh -tA {username}@{hostname} {ssh_command}'.format(
                    username=username, hostname=hostname, ssh_command=ssh_command))
    else:
        click.secho('Server returned status {code}: {text}'.format(code=r.status_code, text=r.text),
                    fg='red', bold=True)

    keyring.set_password(KEYRING_KEY, user, password)

def main():
    cli()

if __name__ == '__main__':
    main()
