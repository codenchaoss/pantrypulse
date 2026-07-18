from datetime import datetime, timezone
import uuid
import threading
from typing import Dict, Any, List

class PrintQueue:
    """
    Simulated in-memory thread-safe print queue.
    Receives menu planner documents (specials, pricing, descriptions) and formats print jobs.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(PrintQueue, cls).__new__(cls, *args, **kwargs)
                cls._instance.jobs = {}
            return cls._instance

    def enqueue(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates a new print job from menu/recipe documents and adds it to the queue.
        """
        job_id = f"job-{uuid.uuid4().hex[:8]}"
        job = {
            "job_id": job_id,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "queued",
            "documents": documents
        }
        self.jobs[job_id] = job
        return job

    def get_status(self, job_id: str) -> Dict[str, Any]:
        """
        Fetches the status of a specific print job.
        """
        return self.jobs.get(job_id, {})

    def list_jobs(self) -> List[Dict[str, Any]]:
        """
        Lists all print jobs in the queue.
        """
        return list(self.jobs.values())

    def clear(self):
        """
        Clears all in-memory jobs (useful for test resets).
        """
        self.jobs.clear()
