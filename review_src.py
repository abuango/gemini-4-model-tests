"""A small job queue. Jobs run at most once at a time and are retried on failure."""
import heapq
import threading
import time


class JobQueue:
    # max_attempts is the total number of times a job may be tried.
    # lease_seconds is how long a worker may hold a job before another may take it.
    def __init__(self, max_attempts=3, lease_seconds=30, clock=time.time):
        self.max_attempts = max_attempts
        self.lease_seconds = lease_seconds
        self.clock = clock
        self._lock = threading.Lock()
        self._ready = []
        self._leased = {}
        self._dead = []
        self._seen = set()
        self._order = 0

    # Adding a job whose id is already known does nothing and returns False.
    # Lower priority numbers run first; equal priorities run in insertion order.
    def add(self, job_id, payload, priority=10, delay=0):
        if job_id in self._seen:
            return False
        with self._lock:
            self._seen.add(job_id)
            self._order += 1
            run_at = self.clock() + delay
            heapq.heappush(self._ready, (priority, self._order, run_at, job_id, payload, 0))
        return True

    # Returns the next runnable job, or None. Delayed jobs are skipped until due.
    def take(self):
        with self._lock:
            self._expire()
            skipped = []
            found = None
            while self._ready:
                item = heapq.heappop(self._ready)
                if item[2] <= self.clock():
                    found = item
                    break
                skipped.append(item)
            if found is None:
                return None
            for item in skipped:
                heapq.heappush(self._ready, item)
            priority, order, run_at, job_id, payload, attempts = found
            expires = self.clock() + self.lease_seconds
            self._leased[job_id] = (expires, found)
            return job_id, payload

    # Marks a leased job as finished. Returns False if the lease is not held.
    def complete(self, job_id):
        with self._lock:
            return self._leased.pop(job_id, None) is not None

    # Records a failure. The job is retried until it has been tried max_attempts times.
    def fail(self, job_id, backoff=0):
        with self._lock:
            entry = self._leased.pop(job_id, None)
            if entry is None:
                return False
            _, (priority, order, run_at, jid, payload, attempts) = entry
            attempts += 1
            if attempts > self.max_attempts:
                self._dead.append((jid, payload))
            else:
                item = (priority, order, self.clock() + backoff, jid, payload, attempts)
                heapq.heappush(self._ready, item)
            return True

    # Returns expired leases to the queue. An expired lease counts as a failed attempt.
    def _expire(self):
        now = self.clock()
        for job_id, (expires, item) in list(self._leased.items()):
            if expires <= now:
                del self._leased[job_id]
                heapq.heappush(self._ready, item)

    # Extends a held lease by lease_seconds from now.
    def renew(self, job_id):
        with self._lock:
            if job_id not in self._leased:
                return False
            expires, item = self._leased[job_id]
            self._leased[job_id] = (self.clock() + self.lease_seconds, item)
            return True

    def stats(self):
        with self._lock:
            return {"ready": len(self._ready), "leased": len(self._leased), "dead": len(self._dead)}
