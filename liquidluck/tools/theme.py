import os
from liquidluck.utils import to_unicode


def __fetch_themes():
    import urllib
    if hasattr(urllib, 'urlopen'):
        urlopen = urllib.urlopen
    else:
        import urllib.request
        urlopen = urllib.request.urlopen

    content = urlopen(
        'https://api.github.com/legacy/repos/search/liquidluck-theme'
    ).read()
    content = to_unicode(content)
    return content


def __load_themes():
    import time
    import tempfile
    path = os.path.join(tempfile.gettempdir(), 'liquidluck.json')

    if not os.path.exists(path) or \
       os.stat(path).st_mtime + 100 < time.time():
        content = __fetch_themes()
        f = open(path, 'w')
        f.write(content)
        f.close()

    content = to_unicode(open(path).read())

    try:
        import json
        json_decode = json.loads
    except ImportError:
        import simplejson
        json_decode = simplejson.loads

    repos = json_decode(content)
    themes = {}
    for theme in repos['repositories']:
        name = theme['name'].replace('liquidluck-theme', '')
        name = name.strip().strip('-')
        theme['name'] = name
        themes[name] = theme
    return themes


SEARCH_TEMPLATE = '''
Theme: %(name)s
Author: %(username)s
Description: %(description)s
Updated: %(pushed)s
URL: %(url)s
'''


def search(keyword=None, clean=False):
    themes = __load_themes()
    available = {}

    if keyword:
        for name in themes:
            if keyword in name:
                available[name] = themes[name]

    for name in (available or themes):
        if clean:
            print(name)
        else:
            theme = themes[name]
            print(SEARCH_TEMPLATE % theme)
    return


def install(keyword):
    themes = __load_themes()
    if keyword not in themes:
        print("can't find theme %s" % keyword)
        return
    theme = themes[keyword]
    repo = theme['url']
    output = '_themes/%s' % keyword
    import subprocess
    subprocess.call(['git', 'clone', repo, output])


if __name__ == '__main__':
    search()
