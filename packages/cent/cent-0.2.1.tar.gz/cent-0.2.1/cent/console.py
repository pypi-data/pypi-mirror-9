#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
import argparse
import os
import sys
import json

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

from .core import Client


def run():

    parser = argparse.ArgumentParser(description='Centrifuge client')

    parser.add_argument(
        'section', metavar='SECTION', type=str, help='section key from cent configuration file'
    )
    parser.add_argument(
        'method', metavar='METHOD', type=str, help='call method'
    )
    parser.add_argument(
        '--params', type=str, help='params data', default='{}'
    )
    parser.add_argument(
        '--config', type=str, default="~/.centrc", help='cent configuration file'
    )

    options = parser.parse_args()

    config_file = os.path.expanduser(options.config)
    config = ConfigParser.ConfigParser()
    config.read(config_file)

    if not options.section in config.sections():
        print(
            "Section {0} not found in {1} configuration file".format(
                options.section, options.config
            )
        )
        sys.exit(1)

    try:
        address = config.get(options.section, 'address')
        project_id = config.get(options.section, 'project_id')
        secret_key = config.get(options.section, 'secret_key')
        try:
            timeout = config.getint(options.section, 'timeout')
        except:
            timeout = 2
    except Exception as e:
        print(e)
        sys.exit(1)

    if not sys.stdin.isatty():
        json_data = sys.stdin.read().strip()
    else:
        json_data = options.params

    if json_data:
        try:
            params = json.loads(json_data)
        except Exception as e:
            print(e)
            sys.exit(1)
    else:
        params = {}

    if not isinstance(params, dict):
        print("params must be dictionary")
        sys.exit(1)

    client = Client(
        address,
        project_id,
        secret_key,
        timeout=timeout
    )

    if not isinstance(params, dict):
        print("params must be valid JSON object")
        sys.exit(1)

    client.add(options.method, params)
    response = client.send()
    result, error = response
    if error:
        print(error)
        sys.exit(1)
    else:
        print(result)


if __name__ == '__main__':
    run()