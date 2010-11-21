from urllib2 import urlopen
from string import ascii_lowercase, digits
from itertools import chain, product, ifilter, islice
import json

try:
    cachef = open("cache", "r")
    try:
        _cache = json.load(cachef)
    except ValueError:
        _cache = {}
    finally:
        cachef.close()
except IOError:
    _cache = {}

def valid(username, token="011b6b129568e20eb9e612c821f719b72775e89d", cache=_cache):
    if cache.has_key(username):
        return cache[username]
    url = "https://twitter.com/users/username_available?username=%(username)s&authenticity_token=%(token)s" % locals()
    retval = json.loads(urlopen(url).read()).get('valid', False)
    cache[username] = retval
    return retval
    
def gen_names(start, end):
    valid_chars = ascii_lowercase + "_" + digits
    return chain(*(map("".join, product(valid_chars, repeat=i)) for i in xrange(start, end + 1)))

def vnames(start, end):
    return ifilter(valid, gen_names(start, end))

if __name__ == "__main__":
    try:
        #print list(islice(vnames(2, 3), 1)) or "nothing found"
        for username in vnames(2, 3):
            print username
        else:
            print " - the end -"
    finally:
        cachef = open("cache", "w")
        try:
            json.dump(_cache, cachef)
        finally:
            cachef.close()
