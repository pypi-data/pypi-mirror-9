def condense(post):
    fb_link = post['actions'][0]['link']

    x = {
        'message': post.get('message'),
        'facebook-link': fb_link,
        'external-link': post.get('link')
    }
    x.update(_parse_from(post))
    yield x

    for comment in post.get('comments', {}).get('data', []):
        x = {
            'message': comment.get('message'),
            'facebook-link': fb_link,
            'external-link': None,
        }
        x.update(_parse_from(comment))
        yield x

def _parse_from(datum):
    return {
        'from-id': datum['from']['id'],
        'from-name': datum['from']['name'],
    }
