import re, csv, sys
from urllib.parse import urlparse

def main():
    sys.stdout.write('<table>\n')
    sys.stdout.write(HEAD)
    for datum in csv.DictReader(sys.stdin):
        datum['external-links'] = find_links(datum)
        for tr in format_body(datum):
            sys.stdout.write(tr)
    sys.stdout.write('</table>\n')

def find_links(datum):
    links = re.findall('https?://[^ ]+', datum['message'])
    if datum['external-link'] and datum['external-link'] not in links:
        links.append(datum['external-link'])
    return links

HEAD = '''
<tr>
  <th>Link</th>
  <th>Posted by</th>
  <th>Original post</th>
</tr>
'''
BODY = '''
<tr>
  <td><a href="%(external-link)s">%(external-link-domain)s</a></td>
  <td><a href="https://facebook.com/%(from-id)s">%(from-name)s</a></td>
  <td><a href="%(facebook-link)s">%(facebook-link-post-id)s</a></td>
</tr>
'''

def format_body(datum):
    args = dict(datum)
    args['facebook-link-post-id'] = datum['facebook-link'].split('/')[-1]
    for external_link in datum['external-links']:
        args['external-link'] = external_link
        args['external-link-domain'] = urlparse(args['external-link']).netloc
        yield (BODY % args).lstrip()

if __name__ == '__main__':
    main()
