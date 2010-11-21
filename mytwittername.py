from Queue import Queue, PriorityQueue
from threading import Thread
from time import time as now
from urllib2 import urlopen
from string import ascii_lowercase, digits
from itertools import chain, product
from functools import partial
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
    
def check_availability(names_queue, available_names_queue):
    while True:
        username = names_queue.get()
        try:
            if valid(username):
                available_names_queue.put(username)
        except Exception, e:
            # I didn't do my job, so I let someone else do it
            available_names_queue.put("[Exception trying to process '%s': %s]" % (username, e.msg))
            names_queue.put(username)
        finally:
            names_queue.task_done()
        
def print_available_names(available_names_queue):
    while True:
        username = available_names_queue.get()
        print username
        available_names_queue.task_done()

if __name__ == "__main__":
    t0 = now()
    try:
        names_queue = PriorityQueue()
        available_names_queue = Queue()
        num_worker_threads = 40
        for i in xrange(num_worker_threads):
             t = Thread(target=partial(check_availability, names_queue, available_names_queue))
             t.daemon = True
             t.start()
        t = Thread(target=partial(print_available_names, available_names_queue))
        t.daemon = True
        t.start()
        
        for name in gen_names(2, 3):
            names_queue.put(name)
        
        names_queue.join()
        available_names_queue.join()
    finally:
        print "All done in %.2f seconds." % (now() - t0)
        cachef = open("cache", "w")
        try:
            json.dump(_cache, cachef)
        finally:
            cachef.close()
