from Queue import Queue, PriorityQueue
from threading import Thread
from time import sleep, time as now
from urllib2 import urlopen
from string import ascii_lowercase, digits
from itertools import chain, product
from functools import partial
from collections import deque
import json
import sys

# Load cache from file, or start fresh
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

def save_cache():
    """Persist cache to disk."""
    sys.stdout.write("[saving cache to disk...]")
    sys.stdout.flush()
    cachef = open("cache", "w")
    try:
        json.dump(_cache, cachef)
    finally:
        cachef.close()
    sys.stdout.write("\bdone]")
    sys.stdout.flush()


def valid(username, token="011b6b129568e20eb9e612c821f719b72775e89d", cache=_cache):
    """Return a boolean whether `username` is available on Twitter."""
    if cache.has_key(username):
        return cache[username]
    url = "https://twitter.com/users/username_available?username=%(username)s&authenticity_token=%(token)s" % locals()
    retval = json.loads(urlopen(url).read()).get('valid', False)
    cache[username] = retval
    return retval


def gen_names(min, max, valid_chars=ascii_lowercase+"_"+digits):
    """Return a lazy sequence of all possible usernames using min up to max characters."""
    return chain(*(map("".join, product(valid_chars, repeat=i)) for i in xrange(min, max + 1)))


def check_availability(names_queue, available_names_queue):
    """This "thread" does the hard work of checking the availability of usernames."""
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
    """This "thread" prints results."""
    def printline(speed, last_names, line_len=79):
        speed = "[%5.2f names/sec]" % speed
        names = ", ".join(last_names)
        if len(names) + len(speed) > line_len:
            names = names[:line_len-len(speed)-3] + "..."
        sys.stdout.write("\r%-*s%s" % (line_len-len(speed), names, speed))
        sys.stdout.flush()
    
    t0 = now()
    counter = 0.0
    last_names = deque(maxlen=15)
    print "Last available usernames:"
    while True:
        username = available_names_queue.get()
        try:
            last_names.appendleft(username)
            counter += 1
            t1 = now() + 1e-5 # avoid division by 0
            
            printline(counter / (t1 - t0), last_names)
        except:
            pass
        finally:
            available_names_queue.task_done()


def main(min=3, max=3, num_worker_threads=40):
    t0 = now()
    
    names_queue = PriorityQueue()
    available_names_queue = Queue()
    
    try:
        # Start worker threads to check username availability.
        for i in xrange(num_worker_threads):
             t = Thread(target=partial(check_availability, names_queue, available_names_queue))
             t.daemon = True
             t.start()
        # Start thread to print available usernames synchronously
        t = Thread(target=partial(print_available_names, available_names_queue))
        t.daemon = True
        t.start()
        
        for name in gen_names(min, max):
            names_queue.put(name)
        
        # Wait without blocking to let user cancel with ctrl-c
        while not names_queue.empty():
            sleep(0.1)
        
        # Block waiting threads processing the last names.
        names_queue.join()
    except KeyboardInterrupt:
        # Will work only before call to join.
        sys.exit(1)
    finally:
        # Block waiting to print all known available names up to now.
        available_names_queue.join()
        print "\nFinished in %.2f seconds." % (now() - t0)
        save_cache()


if __name__ == "__main__":
    main()
