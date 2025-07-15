from print_queue_manager import PrintQueueManager

pq = PrintQueueManager()
pq.enqueue_job("user1", "job1", 1)
pq.tick()
pq.show_status()
