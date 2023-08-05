import urllib.parse as parse


def set_qs_on_url(url, args={}):
    """ Sets the query string on a URL using a dictionary """

    parts = list(parse.urlparse(url))
    parts[4] = parse.urlencode(args)
    return parse.urlunparse(parts)
