# priority_manager.py
from typing import Dict, List, Optional
from datetime import datetime
import threading
import time
from priority_job import PriorityJob, JobStatus
from priority_queue import PriorityQueue

class PriorityManager:
    """Main manager for the priority and aging system"""
    
    def __init__(self, default_aging_interval: int = 300, default_max_wait: int = 3600):
        self.queue = PriorityQueue()
        self.default_aging_interval = default_aging_interval
        self.default_max_wait = default_max_wait
        self._lock = threading.RLock()
        self._running = False
        self._aging_thread = None
    
    def start_aging_system(self):
        """Start the background aging system"""
        if not self._running:
            self._running = True
            self._aging_thread = threading.Thread(target=self._aging_worker, daemon=True)
            self._aging_thread.start()
    
    def stop_aging_system(self):
        """Stop the background aging system"""
        self._running = False
        if self._aging_thread:
            self._aging_thread.join()
    
    def submit_job(self, job_id: str, user_id: str, document_name: str, 
                   pages: int, initial_priority: int = 1,
                   aging_interval: Optional[int] = None,
                   max_wait_time: Optional[int] = None) -> bool:
        """Submit a new print job"""
        with self._lock:
            aging_interval = aging_interval or self.default_aging_interval
            max_wait_time = max_wait_time or self.default_max_wait
            
            job = PriorityJob(
                job_id=job_id,
                user_id=user_id,
                document_name=document_name,
                pages=pages,
                initial_priority=initial_priority,
                aging_interval=aging_interval,
                max_wait_time=max_wait_time
            )
            
            return self.queue.add_job(job)
    
    def get_next_job(self) -> Optional[dict]:
        """Get the next job to process"""
        with self._lock:
            job = self.queue.get_next_job()
            if job:
                return {
                    'job_id': job.job_id,
                    'user_id': job.user_id,
                    'document_name': job.document_name,
                    'pages': job.pages,
                    'current_priority': job.current_priority,
                    'wait_time': job.wait_time_seconds
                }
            return None
    
    def complete_job(self, job_id: str) -> bool:
        """Mark a job as completed and remove from queue"""
        with self._lock:
            completed_job = self.queue.remove_job(job_id)
            return completed_job is not None
    
    def get_queue_status(self) -> dict:
        """Get comprehensive queue status"""
        with self._lock:
            snapshot = self.queue.get_queue_snapshot()
            
            # Calculate statistics
            total_jobs = len(snapshot)
            if total_jobs == 0:
                return {
                    'total_jobs': 0,
                    'avg_wait_time': 0,
                    'priority_distribution': {},
                    'jobs': []
                }
            
            avg_wait = sum(job['wait_time'] for job in snapshot) / total_jobs
            priority_dist = {}
            for job in snapshot:
                priority = job['current_priority']
                priority_dist[priority] = priority_dist.get(priority, 0) + 1
            
            return {
                'total_jobs': total_jobs,
                'avg_wait_time': avg_wait,
                'priority_distribution': priority_dist,
                'jobs': snapshot
            }
    
    def handle_tie_breaking(self, jobs_with_same_priority: List[PriorityJob]) -> PriorityJob:
        """Handle tie-breaking using wait time (FIFO)"""
        return min(jobs_with_same_priority, key=lambda job: job.created_at)
    
    def _aging_worker(self):
        """Background worker for aging system maintenance"""
        while self._running:
            time.sleep(30)  # Check every 30 seconds
            with self._lock:
                # The queue automatically handles aging when accessed
                self.queue.get_queue_snapshot()


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    manager = PriorityManager(aging_interval=60, default_max_wait=1800)  # 1 min aging, 30 min max wait
    manager.start_aging_system()
    
    # Submit some jobs
    manager.submit_job("job1", "user1", "document1.pdf", 10, initial_priority=1)
    manager.submit_job("job2", "user2", "document2.pdf", 5, initial_priority=3)
    manager.submit_job("job3", "user1", "document3.pdf", 20, initial_priority=1)
    
    print("Initial queue status:")
    status = manager.get_queue_status()
    for job in status['jobs']:
        print(f"Job {job['job_id']}: Priority {job['current_priority']}, Wait: {job['wait_time']:.1f}s")
    
    # Simulate some time passing
    time.sleep(2)
    
    print("\nQueue status after waiting:")
    status = manager.get_queue_status()
    for job in status['jobs']:
        print(f"Job {job['job_id']}: Priority {job['current_priority']}, Wait: {job['wait_time']:.1f}s")
    
    manager.stop_aging_system()