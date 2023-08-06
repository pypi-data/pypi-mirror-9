import os, datetime, re
from urllib.parse import urlencode

import vlermv, requests

__all__ = ['download']

GROUP_ID = 1463661227181475
URL = 'https://graph.facebook.com/v2.2/%s/feed' % GROUP_ID
CACHE = os.path.join('~', '.immaterial-digital-labor', 'archive')

def _url(access_token):
    return '%s?access_token=%s' % (URL, access_token)

_dir = os.path.join(CACHE, datetime.date.today().isoformat())
def _transformer(args):
    url = args[0]
    return re.match(r'.*(?:access_token|until)=([^&]+)(?:&.*|)$', url).group(1),
get = vlermv.cache(_dir, transformer = _transformer)(requests.get)

def download(access_token):
    '''
    Return an iterable of "data" entries, each containing the following keys.

    * likes
    * to
    * created_time
    * actions
    * message
    * updated_time
    * comments
    * privacy
    * id
    * from
    * type
    '''

    response = get(_url(access_token))
    while response.ok:
        payload = response.json()
        yield from payload['data']
        if 'paging' in payload:
            response = get(payload['paging']['next'])
        else:
            break
