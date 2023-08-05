# -*- coding: utf-8 -*-
from fs.server import Server
from twisted.internet import reactor
from twisted.python import log
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root_folder')
    parser.add_argument('root_url')
    parser.add_argument('auth_server')
    parser.add_argument('max_bucket_size', type=int)
    parser.add_argument('max_file_size', type=int)
    parser.add_argument('--port', default=9000, type=int)
    parser.add_argument('-v', '--verbose', default=False, action='store_true', dest='verbose')
    args = parser.parse_args()
    
    if args.verbose:
        log.startLogging(sys.stdout)
    
    server = Server(
        root_folder=args.root_folder,
        root_url=args.root_url,
        auth_server=args.auth_server,
        max_bucket_size=args.max_bucket_size,
        max_file_size=args.max_file_size)
    reactor.listenTCP(args.port, server)
    reactor.run()
