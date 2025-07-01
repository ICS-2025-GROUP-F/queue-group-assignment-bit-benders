class PrintQueueManager:
    def __init__(self, *, aging_interval=3, expiry_time=10, capacity=50):
        self.queue = []
        self.current_time = 0
        self.aging_interval = aging_interval
        self.expiry_time = expiry_time
        self.capacity = capacity

    def enqueue_job(self, user_id, job_id, priority):
        if len(self.queue) >= self.capacity:
            print("Queue full – job rejected.")
            return False

        job = {
            "user_id": user_id,
            "job_id": job_id,
            "priority": priority,
            "waiting_time": 0,
            "last_aged": 0
        }
        self.queue.append(job)
        self._resort()
        return True

    def tick(self):
        self.current_time += 1
        for job in self.queue:
            job["waiting_time"] += 1
        self._apply_priority_aging()
        self._remove_expired_jobs()
        self._resort()
        print(f"Tick {self.current_time} complete.")

    def _apply_priority_aging(self):
        if not self.aging_interval:
            return
        bumped = False
        for job in self.queue:
            if job["waiting_time"] - job["last_aged"] >= self.aging_interval:
                job["priority"] += 1
                job["last_aged"] = job["waiting_time"]
                bumped = True
        if bumped:
            print("Priority aging applied.")

    def _remove_expired_jobs(self):
        if not self.expiry_time:
            return
        before = len(self.queue)
        self.queue = [
            job for job in self.queue
            if job["waiting_time"] < self.expiry_time
        ]
        removed = before - len(self.queue)
        if removed:
            print(f"{removed} job(s) expired.")

    def _resort(self):
        self.queue.sort(key=lambda j: (-j["priority"], j["waiting_time"]))

    def show_status(self):
        print(f"\n--- Queue at tick {self.current_time} ---")
        if not self.queue:
            print("[empty]\n")
            return
        for pos, job in enumerate(self.queue, 1):
            print(f"{pos:>2}. Job {job['job_id']:>5} | User {job['user_id']:<8} | "
                  f"P={job['priority']} | waited {job['waiting_time']} t")
        print()

if __name__ == "__main__":
    pq = PrintQueueManager(aging_interval=3, expiry_time=10)
    pq.enqueue_job("user1", "job1", 1)
    pq.enqueue_job("user2", "job2", 2)

    for t in range(1, 13):
        pq.tick()
        if t == 5:
            pq.enqueue_job("user3", "job3", 1)
        if t == 7:
            pq.queue.pop(0)
        pq.show_status()
