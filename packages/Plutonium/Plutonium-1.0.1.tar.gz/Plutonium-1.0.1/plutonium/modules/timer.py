from threading import Thread, Event

class Timer(Thread):
    def __init__(self, interval, callback):
        super(Timer, self).__init__()

        self.interval_event = Event()
        self.main_event = Event()
        self.interval = interval
        self.callback = callback

        self.daemon = True # stop if the program exits

        super(Timer, self).start()

    def run(self):
        while self.main_event.wait():
            while not self.interval_event.wait(self.interval):
                self.callback()

    def start(self, interval = None):
        if interval is not None:
            self.interval = interval
        self.interval_event.clear()
        self.main_event.set()

    def stop(self):
        self.interval_event.set()
