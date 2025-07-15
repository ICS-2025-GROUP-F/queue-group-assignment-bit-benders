# priority_queue.py
import heapq
from typing import List, Optional, Tuple
from priority_job import PriorityJob, JobStatus

class PriorityQueue:
    """Priority queue with aging support for print jobs"""
    
    def __init__(self):
        self._heap: List[Tuple[int, float, PriorityJob]] = []
        self._job_lookup = {}  # job_id -> job mapping for quick access
        self._counter = 0  # For tie-breaking
    
    def add_job(self, job: PriorityJob) -> bool:
        """Add a job to the priority queue"""
        if job.job_id in self._job_lookup:
            return False  # Job already exists
        
        # Use negative priority for max-heap behavior (higher priority = lower number)
        # Use creation time as secondary sort (FIFO for same priority)
        priority_key = (-job.current_priority, job.created_at.timestamp(), self._counter)
        heapq.heappush(self._heap, (priority_key, job))
        
        self._job_lookup[job.job_id] = job
        self._counter += 1
        return True
    
    def get_next_job(self) -> Optional[PriorityJob]:
        """Get the highest priority job (doesn't remove it)"""
        self._cleanup_expired_jobs()
        self._rebalance_priorities()
        
        if not self._heap:
            return None
        
        _, job = self._heap[0]
        return job if job.status == JobStatus.PENDING else None
    
    def remove_job(self, job_id: str) -> Optional[PriorityJob]:
        """Remove and return a specific job"""
        if job_id not in self._job_lookup:
            return None
        
        job = self._job_lookup.pop(job_id)
        job.status = JobStatus.COMPLETED
        
        # Rebuild heap without the removed job
        self._rebuild_heap()
        return job
    
    def _cleanup_expired_jobs(self):
        """Remove expired jobs from the queue"""
        expired_jobs = []
        for job_id, job in self._job_lookup.items():
            if job.is_expired and job.status == JobStatus.PENDING:
                job.status = JobStatus.EXPIRED
                expired_jobs.append(job_id)
        
        for job_id in expired_jobs:
            del self._job_lookup[job_id]
        
        if expired_jobs:
            self._rebuild_heap()
    
    def _rebalance_priorities(self):
        """Rebalance heap when priorities have changed due to aging"""
        needs_rebalance = False
        
        for _, job in self._heap:
            if job.status == JobStatus.PENDING:
                # Check if current priority differs significantly from heap position
                needs_rebalance = True
                break
        
        if needs_rebalance:
            self._rebuild_heap()
    
    def _rebuild_heap(self):
        """Rebuild the heap with current priorities"""
        active_jobs = [job for job in self._job_lookup.values() 
                      if job.status == JobStatus.PENDING]
        
        self._heap.clear()
        for job in active_jobs:
            priority_key = (-job.current_priority, job.created_at.timestamp(), self._counter)
            heapq.heappush(self._heap, (priority_key, job))
            self._counter += 1
    
    def get_queue_snapshot(self) -> List[dict]:
        """Get current queue state for visualization"""
        self._cleanup_expired_jobs()
        self._rebalance_priorities()
        
        snapshot = []
        for _, job in sorted(self._heap):
            if job.status == JobStatus.PENDING:
                snapshot.append({
                    'job_id': job.job_id,
                    'user_id': job.user_id,
                    'document_name': job.document_name,
                    'initial_priority': job.initial_priority,
                    'current_priority': job.current_priority,
                    'wait_time': job.wait_time_seconds,
                    'pages': job.pages,
                    'created_at': job.created_at.isoformat()
                })
        
        return snapshot
    
    def size(self) -> int:
        """Get number of pending jobs"""
        return len([job for job in self._job_lookup.values() 
                   if job.status == JobStatus.PENDING])