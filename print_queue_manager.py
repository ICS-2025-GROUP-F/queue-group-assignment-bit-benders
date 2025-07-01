class PrintJob:
    def enqueue_job(self, user_id, job_id, priority, waiting_time=0):
        self.user_id = user_id
        self.job_id = job_id
        self.priority = priority
        self.waiting_time = waiting_time

    def _str_(self):
        return f"(User: {self.user_id}, Job: {self.job_id}, Priority: {self.priority}, Waiting: {self.waiting_time}s)"


class CircularQueue:
    def _init_(self, capacity):
        self.capacity = capacity
        self.queue = []
        for _ in range(capacity):
            self.queue.append(None)
        self.front = -1
        self.rear = -1
        self.size = 0

    def is_full(self):
        return self.size == self.capacity

    def is_empty(self):
        return self.size == 0

    def enqueue(self, job):
        if self.is_full():
            print("Queue is full. Cannot add job.")
            return False

        if self.front == -1:
            self.front = 0

        self.rear = (self.rear + 1) % self.capacity
        self.queue[self.rear] = job
        self.size += 1
        print(f"Enqueued: {job}")
        return True

    def dequeue(self):
        if self.is_empty():
            print("Queue is empty. Cannot dequeue.")
            return None

        job = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.size -= 1

        if self.size == 0:
            self.front = -1
            self.rear = -1

        print(f"Dequeued: {job}")
        return job

    def status(self):
        print("Queue Status:")
        if self.is_empty():
            print("Empty")
            return

        index = self.front
        for _ in range(self.size):
            print(f"  {self.queue[index]}")
            index = (index + 1) % self.capacity