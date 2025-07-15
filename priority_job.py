# priority_job.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    EXPIRED = "expired"

@dataclass
class PriorityJob:
    """Represents a print job with priority and aging capabilities"""
    job_id: str
    user_id: str
    document_name: str
    pages: int
    initial_priority: int = 1  # 1 = lowest, 5 = highest
    created_at: datetime = None
    status: JobStatus = JobStatus.PENDING
    aging_interval: int = 300  # seconds (5 minutes default)
    max_wait_time: int = 3600  # seconds (1 hour default)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def current_priority(self) -> int:
        """Calculate current priority based on aging"""
        if self.status != JobStatus.PENDING:
            return self.initial_priority
            
        time_waited = datetime.now() - self.created_at
        aging_increments = int(time_waited.total_seconds() // self.aging_interval)
        
        # Cap priority at 5 (highest)
        return min(5, self.initial_priority + aging_increments)
    
    @property
    def is_expired(self) -> bool:
        """Check if job has exceeded maximum wait time"""
        time_waited = datetime.now() - self.created_at
        return time_waited.total_seconds() > self.max_wait_time
    
    @property
    def wait_time_seconds(self) -> float:
        """Get current wait time in seconds"""
        return (datetime.now() - self.created_at).total_seconds()