import argparse
from .download import download
from .condense import condense

ACCESS_TOKEN_MESSAGE = '''
Go to this address, get an access token, and paste it below.
https://developers.facebook.com/tools/explorer/

'''
FIELDNAMES = [
    'message',
    'facebook-link', 'external-link',
    'from-id', 'from-name',
]

def parse_args():
    p = argparse.ArgumentParser(
        description = 'Download links from the Immaterial Digital Labor group, '\
                      'and present them in some presentable way.',
    )
    p.add_argument('--access_token')

    _args = p.parse_args()
    if None == _args.access_token:
        _args.access_token = input(ACCESS_TOKEN_MESSAGE)
    return _args

def cli():
    import csv, sys
    args = parse_args()
    w = csv.DictWriter(sys.stdout, FIELDNAMES)
    w.writeheader()
    for post in download(args.access_token):
        w.writerows(condense(post))
