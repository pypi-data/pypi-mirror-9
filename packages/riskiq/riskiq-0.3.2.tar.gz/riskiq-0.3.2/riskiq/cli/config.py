from riskiq.config import Config
from riskiq.output import GenericOutput
from argparse import ArgumentParser
import sys


def main():
    parser = ArgumentParser()
    parser.add_argument('-t', '--token', help='API token')
    parser.add_argument('-k', '--key', help='API private key')
    parser.add_argument('--http-proxy', default='',
        help='proxy to use for http requests')
    parser.add_argument('--https-proxy', default='',
        help='proxy to use for https requests')
    parser.add_argument('-p', '--print', action='store_true', 
        dest='show_config', help='Show current API configuration')
    args = parser.parse_args()
    if args.show_config:
        config = Config()
        show_config(config)
        sys.exit(0)
    config_options = {}
    if not args.token or not args.key:
        parser.error("provide API token and secret key to configure client")
    config_options['api_token'] = args.token
    config_options['api_private_key'] = args.key
    config_options['http_proxy'] = args.http_proxy
    config_options['https_proxy'] = args.https_proxy
    config = Config(**config_options)
    show_config(config)
    sys.exit(0)


def show_config(config):
    print "\nCurrent Configuration:\n"
    for k, v in sorted(config.config.items()):
        print "%15s: %s" % (k, v)

if __name__ == '__main__':
    main()

