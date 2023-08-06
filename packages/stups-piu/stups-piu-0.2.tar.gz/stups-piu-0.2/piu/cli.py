#!/usr/bin/env python3
'''
Helper script to request access to a certain host.
'''

import click
import ipaddress
import json
import keyring
import os
import requests
import yaml


KEYRING_KEY = 'piu'

CONFIG_DIR_PATH = click.get_app_dir('piu')
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'piu.yaml')

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

STUPS_CIDR = ipaddress.ip_network('172.31.0.0/16')


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('host', metavar='[USER]@HOST')
@click.argument('reason')
@click.argument('reason_cont', nargs=-1, metavar='[..]')
@click.option('-u', '--user', help='Username to use for authentication', envvar='USER')
@click.option('-p', '--password', help='Password to use for authentication', envvar='PIU_PASSWORD')
@click.option('-E', '--even-url', help='Even SSH Access Granting Service URL', envvar='EVEN_URL')
@click.option('-O', '--odd-host', help='Odd SSH bastion hostname', envvar='ODD_HOST')
@click.option('--insecure', help='Do not verify SSL certificate', is_flag=True, default=False)
def cli(host, user, password, even_url, odd_host, reason, reason_cont, insecure):
    # sdf
    parts = host.split('@')
    if len(parts) > 1:
        username = parts[0]
    else:
        username = user

    hostname = parts[-1]

    reason = ' '.join([reason] + list(reason_cont)).strip()

    cacert = not insecure

    if not even_url:
        if not os.path.exists(CONFIG_FILE_PATH):
            os.makedirs(CONFIG_DIR_PATH, exist_ok=True)
            even_url = click.prompt('Please enter the Even SSH access granting service URL')
            config = {'even_url': even_url}
            with open(CONFIG_FILE_PATH, 'w') as fd:
                yaml.dump(config, fd)

        with open(CONFIG_FILE_PATH, 'rb') as fd:
            config = yaml.safe_load(fd)
        even_url = config['even_url']
        if 'cacert' in config:
            cacert = config['cacert']

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        ip = None

    if ip and ip in STUPS_CIDR and not odd_host:
        odd_host = click.prompt('Please enter the Odd SSH bastion hostname')

    password = password or keyring.get_password(KEYRING_KEY, user)

    if not password:
        password = click.prompt('Password', hide_input=True)

    if not even_url.endswith('/access-requests'):
        even_url = even_url.rstrip('/') + '/access-requests'

    first_host = hostname
    if odd_host:
        first_host = odd_host

    data = {'username': username, 'hostname': first_host, 'reason': reason}
    if odd_host:
        data['remote-host'] = hostname
    click.secho('Requesting access to host {hostname} for {username}..'.format(**vars()), bold=True)
    r = requests.post(even_url, headers={'Content-Type': 'application/json'},
                      data=json.dumps(data), auth=(user, password),
                      verify=cacert)
    if r.status_code == 200:
        click.secho(r.text, fg='green', bold=True)
        ssh_command = ''
        if odd_host:
            ssh_command = 'ssh {username}@{hostname}'.format(**vars())
        click.secho('You can now access your server with the following command:')
        click.secho('ssh -tA {username}@{first_host} {ssh_command}'.format(
                    username=username, first_host=first_host, ssh_command=ssh_command))
    else:
        click.secho('Server returned status {code}: {text}'.format(code=r.status_code, text=r.text),
                    fg='red', bold=True)

    keyring.set_password(KEYRING_KEY, user, password)

def main():
    cli()

if __name__ == '__main__':
    main()
