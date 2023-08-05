# -*- coding:utf-8 -*-
import argparse

import api
import sshconfig


def make_config():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()

    getter = sub.add_parser('echo')
    getter.add_argument('filepath')
    getter.set_defaults(func=api.echo)

    getter = sub.add_parser('get')
    getter.add_argument('filepath')
    getter.add_argument('host')
    getter.set_defaults(func=api.download_from_github)

    putter = sub.add_parser('put', help='Put file \'authorized_keys\' to remote host.')
    putter.add_argument('hosts', nargs='*')
    putter.add_argument('-t', '--tag', dest='tag')
    parser.add_argument('-q', '--quiet', dest='quiet',
                        action='store_true', default=False)
    putter.add_argument('-s', '--src-file', dest='keyfile',
                        help='Filepath of \'authorized_keys\' file to be put.')
    putter.add_argument('-e', '--env-file', dest='filepath',
                        help='Filepath of host data file written as YAML format.\n'
                             'Extract user keyfiles from Github when specified this option.')
    putter.set_defaults(func=api.put_authorized_keys)

    setup = sub.add_parser('config')
    setup.add_argument('filepath')
    setup.add_argument('-t', '--tag', nargs='+', dest='tags', default=None)
    setup.set_defaults(func=sshconfig.generate)

    return parser.parse_args()


def main():
    config = make_config()
    config.func(config)


if __name__ == '__main__':
    main()
