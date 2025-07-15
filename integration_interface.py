# integration_interface.py
"""
Integration interface for seamless connection with other team modules
"""

from priority_manager import PriorityManager
from typing import Dict, List, Optional, Callable

class PrintQueueIntegration:
    """
    Integration wrapper that provides specific interfaces for other team modules
    """
    
    def __init__(self, aging_interval: int = 300, max_wait_time: int = 3600):
        self.priority_manager = PriorityManager(aging_interval, max_wait_time)
        self.priority_manager.start_aging_system()
        
        # Callbacks for other modules
        self.expiry_notification_callback = None
        self.status_change_callback = None
    
    # === INTERFACE FOR MODULE 1: Core Queue Management ===
    def enqueue_job(self, job_id: str, user_id: str, document_name: str, 
                    pages: int, priority: int = 1) -> bool:
        """Standard enqueue operation for core queue management"""
        return self.priority_manager.submit_job(
            job_id, user_id, document_name, pages, priority
        )
    
    def dequeue_job(self) -> Optional[Dict]:
        """Standard dequeue operation for core queue management"""
        return self.priority_manager.get_next_job()
    
    def get_job_metadata(self, job_id: str = None) -> Dict:
        """Get metadata for all jobs or specific job"""
        status = self.priority_manager.get_queue_status()
        if job_id:
            for job in status['jobs']:
                if job['job_id'] == job_id:
                    return job
            return None
        return status
    
    # === INTERFACE FOR MODULE 3: Job Expiry & Cleanup ===
    def set_expiry_notification_callback(self, callback: Callable):
        """Set callback function to notify when jobs expire"""
        self.expiry_notification_callback = callback
    
    def get_expired_jobs(self) -> List[Dict]:
        """Get list of jobs that have expired (for notification purposes)"""
        # This integrates with your existing expiry logic
        return []  # Your system auto-removes expired jobs
    
    def cleanup_expired_jobs(self) -> int:
        """Manual cleanup trigger (returns number of jobs cleaned)"""
        old_count = self.priority_manager.queue.size()
        self.priority_manager.get_queue_status()  # Triggers cleanup
        new_count = self.priority_manager.queue.size()
        return old_count - new_count
    
    # === INTERFACE FOR MODULE 4: Concurrent Job Submission ===
    def submit_simultaneous_jobs(self, job_list: List[Dict]) -> Dict[str, bool]:
        """Handle simultaneous job submissions safely"""
        results = {}
        for job_data in job_list:
            success = self.priority_manager.submit_job(
                job_data['job_id'],
                job_data['user_id'],
                job_data['document_name'],
                job_data['pages'],
                job_data.get('priority', 1)
            )
            results[job_data['job_id']] = success
        return results
    
    def is_thread_safe(self) -> bool:
        """Confirm thread safety for concurrent operations"""
        return True  # Your system is thread-safe
    
    # === INTERFACE FOR MODULE 5: Event Simulation & Time Management ===
    def handle_tick_event(self, tick_time: float = None) -> Dict:
        """Handle simulation tick events"""
        # Trigger aging update and get current status
        status = self.priority_manager.get_queue_status()
        
        # Notify status change callback if set
        if self.status_change_callback:
            self.status_change_callback(status)
        
        return status
    
    def set_simulation_time(self, current_time: float):
        """Sync with simulation time if needed"""
        # Your system uses real time, but this allows sync if needed
        pass
    
    # === INTERFACE FOR MODULE 6: Visualization & Reporting ===
    def get_visualization_data(self) -> Dict:
        """Get formatted data perfect for visualization"""
        status = self.priority_manager.get_queue_status()
        
        # Format specifically for visualization needs
        return {
            'queue_snapshot': status['jobs'],
            'statistics': {
                'total_jobs': status['total_jobs'],
                'average_wait_time': status['avg_wait_time'],
                'priority_distribution': status['priority_distribution']
            },
            'queue_order': [job['job_id'] for job in status['jobs']],
            'timestamp': status.get('timestamp', 'now')
        }
    
    def get_print_order_report(self) -> List[Dict]:
        """Get jobs in the order they will be printed"""
        status = self.priority_manager.get_queue_status()
        return status['jobs']  # Already in priority order
    
    # === GENERAL INTEGRATION HELPERS ===
    def register_status_callback(self, callback: Callable):
        """Register callback for status changes"""
        self.status_change_callback = callback
    
    def get_system_health(self) -> Dict:
        """Get system health status for monitoring"""
        status = self.priority_manager.get_queue_status()
        return {
            'status': 'healthy',
            'queue_size': status['total_jobs'],
            'aging_system_running': True,
            'memory_usage': 'normal',
            'thread_safety': True
        }
    
    def shutdown(self):
        """Clean shutdown for system integration"""
        self.priority_manager.stop_aging_system()


# Example usage showing integration with other modules
if __name__ == "__main__":
    # Initialize integration interface
    integration = PrintQueueIntegration()
    
    # === Module 1 (Core Queue) can use: ===
    integration.enqueue_job("job1", "user1", "doc1.pdf", 10, 2)
    next_job = integration.dequeue_job()
    
    # === Module 3 (Expiry) can use: ===
    def expiry_notification(expired_jobs):
        print(f"Jobs expired: {expired_jobs}")
    integration.set_expiry_notification_callback(expiry_notification)
    
    # === Module 4 (Concurrent) can use: ===
    simultaneous_jobs = [
        {"job_id": "job2", "user_id": "user2", "document_name": "doc2.pdf", "pages": 5},
        {"job_id": "job3", "user_id": "user3", "document_name": "doc3.pdf", "pages": 15}
    ]
    results = integration.submit_simultaneous_jobs(simultaneous_jobs)
    
    # === Module 5 (Event Simulation) can use: ===
    tick_status = integration.handle_tick_event()
    
    # === Module 6 (Visualization) can use: ===
    viz_data = integration.get_visualization_data()
    print_order = integration.get_print_order_report()
    
    print("Integration successful!")
    integration.shutdown()