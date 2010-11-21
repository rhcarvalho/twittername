from Queue import Queue
from threading import Thread
from time import sleep, time as now
from random import uniform

t0 = now()

def worker(id):
    def workfunc():
        while True:
            item = q.get()
            t = uniform(1, 5)
            sleep(t)
            print "Thread <%2s> processed item <%2s> in %.2f seconds." % (id, item, t)
            q.task_done()
    return workfunc

q = Queue()
num_worker_threads = 2
for i in range(num_worker_threads):
     t = Thread(target=worker(i))
     t.daemon = True
     t.start()

source = range(20)
 
for item in source:
    q.put(item)

q.join()       # block until all tasks are done
print "All done in %.2f seconds." % (now() - t0)
