#!/usr/bin/env python
import os, sys, argparse, datetime
from yaml import load
from bottle import route, abort, run, request



def main():
    """ Run simple server """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--config',
        required=True,
        help='Path to config.yml (required)'
    )
    parser.add_argument('--host', help="Run on host. Default: '0.0.0.0'")
    parser.add_argument('--port', help="Run on port. Default: 3456")
    args = parser.parse_args(sys.argv[1:])

    config = args.config
    if not os.path.isfile(config):
        raise ValueError('Unable to find specified config [%s]' % config)

    host = '0.0.0.0'
    if args.host:
        host = args.host

    port = 34567
    if args.port:
        port = args.port

    with open(config, 'r') as yml:
        config = load(yml)

    apps = config.get('apps', [])
    allowed = config.get('allowed-hosts', [])
    host = config.get('host', host)
    port = config.get('port', port)

    @route('/')
    @route('/<app>', method=['GET'])
    @route('/<app>', method=['POST'])
    @route('/<app>/', method=['GET'])
    @route('/<app>/', method=['POST'])
    def welcome(app=None):
        if not app:
            return "Welcome to poke!"

        ip = request.environ.get('REMOTE_ADDR')
        if ip not in allowed:
            abort(403, "Access from %s is forbidden" % ip)
        if app not in apps:
            raise abort(404, 'Unknown application')

        poked = False
        for file in apps[app]:
            with open(file, 'a'):
                os.utime(file, None)
                poked = True


        if poked:
            return "Poked [%s] @ %s" % (app, datetime.datetime.now())
        else:
            return "No files to touch"

    run(host=host, port=port)

if __name__ == '__main__':
    main()