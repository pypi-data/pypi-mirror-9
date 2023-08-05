# -*- coding:utf-8 -*-
import sys
import codecs
import socket
from os.path import expanduser
from contextlib import closing
from tempfile import NamedTemporaryFile
from getpass import getpass

import paramiko
from paramiko.ssh_exception import AuthenticationException
import requests

import publickey.yamldata as yd


def connect_params(config, host):
    _, params = config.lookup(host), {}

    def value_if(x, y, func=None):
        if x in _:
            params[y] = _[x] if not func else func(_[x])

    value_if('hostname', 'hostname')
    value_if('user', 'username')
    value_if('port', 'port', int)
    return params


def challenge_to_connect(client, params, quiet, yamlpath=None):
    try:
        client.connect(**params)
    except socket.gaierror:
        # Name or host not known.
        if quiet or not yamlpath:
            raise
        host = yd.load(yamlpath)[params['hostname']]
        params['hostname'] = host['hostname']
        challenge_to_connect(client, params, quiet, yamlpath=None)
    except AuthenticationException:
        if quiet:
            raise
        if 'username' not in params:
            params['username'] = raw_input('username: ')
        password = getpass('%s@%s\'s password: ' % (
            params['username'], params['hostname']
        ))
        client.connect(
            password=password,
            **params
        )


def echo(config):
    filepath = config.filepath
    quiet = config.quiet
    assert filepath
    doc = yd.load(filepath)
    stdout = sys.stdout

    with open(expanduser('~/.ssh/config'), 'r') as fp:
        config = paramiko.SSHConfig()
        config.parse(fp)

    with closing(paramiko.SSHClient()) as client:
        client.load_host_keys(expanduser('~/.ssh/known_hosts'))
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        items = [(yd.first_tag(x), name, x) for name, x in yd._all(doc)]
        for envname, name, dct in sorted(items, key=lambda x: x[0]):
            params = connect_params(config, name)
            stdout.write('%s: %s/%s ==> ' % (envname, name, dct['hostname']))
            try:
                challenge_to_connect(client, params, quiet)
            except:
                stdout.write('Failed\n')
            else:
                stdout.write('OK\n')


def put_authorized_keys(config):
    stdout = codecs.getwriter('utf-8')(sys.stdout)
    keyfile = config.keyfile
    filepath = config.filepath
    tag = config.tag
    quiet = config.quiet
    hosts = config.hosts

    assert bool(keyfile) ^ bool(filepath)
    assert bool(tag) ^ bool(hosts)
    if tag:
        assert filepath
        doc = yd.load(filepath)
        hosts = [name for name, _ in yd.filter_by_tags(doc, [tag])]

    with open(expanduser('~/.ssh/config'), 'r') as fp:
        config = paramiko.SSHConfig()
        config.parse(fp)

    stdout.write('***** Start deploying authorized_keys *****\n')
    with closing(paramiko.SSHClient()) as client:
        client.load_host_keys(expanduser('~/.ssh/known_hosts'))
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        for host in hosts:
            params = connect_params(config, host)
            challenge_to_connect(client, params, quiet, filepath)
            if filepath:
                temp = NamedTemporaryFile()
                stdout.write(
                    '    ==> downloading \'%s/%s\' members publickeys '
                    'from github.com.\n' %
                    (host, params['hostname'])
                )
                _download_from_github(filepath, host, dest=temp)
                temp.seek(0)
                authorized_keys = temp.name
            else:
                authorized_keys = keyfile

            with closing(client.open_sftp()) as sftp:
                stdout.write(
                    '    ==> uploading authorized_keys to \'%s/%s\'.\n' %
                    (host, params['hostname'])
                )
                sftp.put(authorized_keys, '.ssh/authorized_keys')
    stdout.write('***** Finished *****\n')


def download_from_github(config, dest=None):
    return _download_from_github(config.filepath, config.host, dest)


def _download_from_github(filepath, host, dest):
    if not dest:
        dest = sys.stdout

    doc = yd.load(filepath)

    def _members(host):
        data = doc[host]
        assert 'members' in data
        return data['members']

    members = _members(host)
    for keystring in iterkeystrings(members):
        dest.write(keystring)


def iterkeystrings(members):
    for member in members:
        url = 'https://github.com/{0}.keys'.format(member)
        with closing(requests.get(url)) as response:
            assert response.ok
            items = enumerate(response.text.split('\n'), start=1)
            for number, line in items:
                yield '{0} {1}@github.com.{2}\n'.format(
                    line, member, number
                )
