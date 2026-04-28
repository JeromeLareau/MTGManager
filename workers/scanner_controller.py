import time

class ScanController:
    def __init__(self):
        self.busy = False
        self.last_attempt = 0
        self.retry_delay = 1.0

    def can_submit(self):
        if self.busy:
            return False
        if time.time() - self.last_attempt < self.retry_delay:
            return False
        return True

    def mark_submitted(self):
        self.busy = True
        self.last_attempt = time.time()

    def mark_done(self):
        self.busy = False
