#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler

SUPPORTED_HOOKS = ['github']

def parse_args():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--type', '-t', type=str, help='type of hook to run', choices=SUPPORTED_HOOKS, default='github')
    parser.add_argument('--directory', '-d', type=str, help='working directory to run the command')
    parser.add_argument('--host', '-H', help='host to run on', default='')
    parser.add_argument('--port', '-p', type=int, help='port to run on', default=8000)
    parser.add_argument('command', nargs='*', help='command to run', default=['git', 'pull', 'origin', 'master'])

    return parser.parse_args()

def run_server(command, kind, cwd, address):
    class GitHubHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            from subprocess import Popen

            body = self.rfile.read(int(self.headers['Content-Length']))
            valid = request_is_valid(self.headers['X-Hub-Signature'].replace('sha1=', ''), body)

            self.send_response(200 if valid else 403)
            self.end_headers()

            if valid:
                Popen(command, cwd=cwd)

    if kind == 'github':
        handler = GitHubHandler
    else:
        raise Exception('Unknown Handler "' + kind + '"')

    httpd = HTTPServer(address, handler)
    print('Serving on {0}:{1}'.format(address[0], address[1]))
    httpd.serve_forever()

def create_secret():
    from random import choice
    from string import hexdigits
    from os.path import isfile

    if not isfile('.pull_hook_secret'):
        with open('.pull_hook_secret', 'w') as f:
            secret = ''.join(choice(hexdigits) for _ in range(20))
            print('Created new key with value: ' + secret)
            f.write(secret)

def request_is_valid(signature, body):
    from hashlib import sha1
    import hmac

    with open('.pull_hook_secret') as f:
        secret = bytearray(f.read(), 'utf-8')
        hashed = bytearray(hmac.new(secret, body, sha1).hexdigest(), 'utf-8')
        bitten = bytearray(signature, 'utf-8')

        return hmac.compare_digest(hashed, bitten)

def main():
    args = parse_args()
    address = (args.host, args.port)
    create_secret()
    run_server(args.command, args.type, args.directory, address)
