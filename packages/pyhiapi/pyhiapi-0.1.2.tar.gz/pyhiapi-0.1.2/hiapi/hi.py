#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hi!\n'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bind-address',
                        dest='bind', default='127.0.0.1')
    parser.add_argument('-p', '--port', dest='port', default=4000, type=int)
    return parser.parse_args()

def main():
    opts = parse_args()
    app.run(host=opts.bind, port=opts.port)

if __name__ == "__main__":
    main()
