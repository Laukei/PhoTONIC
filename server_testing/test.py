import threading
import time 
from queue import Queue, Empty

def launch_monitor_in_thread(anc350):
    queue = Queue()
    monitor = ANC350Monitor(queue,anc350)
    monitor.start()
    return monitor, queue



class ANC350Monitor(threading.Thread):
    def __init__(self, queue, anc350):
        super().__init__()
        self.anc350 = anc350
        self.queue = queue
        self.daemon = True

    def run(self):
        print('just running')
        print(threading.currentThread().getName())
        while True:
            try:
                val = self.queue.get_nowait()
                print('val: {}'.format(val))
                self.do_thing_with_message(val)
            except Empty:
                pass
            time.sleep(0.01)


    def do_thing_with_message(self, message):
        print(threading.currentThread().getName(), "Received {}".format(message))
        self.queue.put('hi back')


if __name__ == '__main__':
    monitor, q = launch_monitor_in_thread(None)
    time.sleep(0.1)
    monitor.queue.put("Print this!")
    print(q.get())