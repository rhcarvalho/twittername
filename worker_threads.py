from Queue import PriorityQueue
from threading import Thread, active_count
from time import sleep, time as now
from random import uniform

t0 = now()

def worker(id):
    def workfunc():
        while True:
            item = q.get()
            try:
                t = uniform(1, 3)
                sleep(t)
                if item == 7:
                    print "[Thread %s] I cannot process item %s." % (id, item)
                    raise Exception
                print "Thread <%2s> processed item <%2s> in %.2f seconds. Active threads: %d." % (id, item, t, active_count())
            except:
                # I didn't do my job, so I let someone else do it
                q.put(item + 0.1)
            finally:
                q.task_done()
    return workfunc

q = PriorityQueue()
num_worker_threads = 5
for i in range(num_worker_threads):
     t = Thread(target=worker(i))
     t.daemon = True
     t.start()

source = range(20)
 
for item in source:
    q.put(item)

q.join()       # block until all tasks are done
print "All done in %.2f seconds." % (now() - t0)
