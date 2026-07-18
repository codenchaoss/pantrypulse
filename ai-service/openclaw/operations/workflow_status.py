from datetime import datetime, timezone
import uuid
import threading
from typing import Dict, Any, List

class WorkflowStatusTracker:
    """
    Simulated in-memory thread-safe workflow lifecycle status tracker.
    States: PENDING, RUNNING, PARTIAL_SUCCESS, COMPLETED, FAILED.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(WorkflowStatusTracker, cls).__new__(cls, *args, **kwargs)
                cls._instance.states = {}
            return cls._instance

    def create_workflow(self) -> str:
        """
        Registers a new workflow run and sets status to PENDING.
        """
        w_id = f"wflow-{uuid.uuid4().hex[:8]}"
        self.states[w_id] = {
            "workflow_id": w_id,
            "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "completed_at": None,
            "status": "PENDING",
            "warnings": []
        }
        return w_id

    def update_status(self, w_id: str, status: str, warnings: List[str] = None):
        """
        Updates status and appends any warning logs.
        """
        if w_id in self.states:
            self.states[w_id]["status"] = status
            if warnings:
                self.states[w_id]["warnings"].extend(warnings)
            if status in ["COMPLETED", "PARTIAL_SUCCESS", "FAILED"]:
                self.states[w_id]["completed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_status(self, w_id: str) -> Dict[str, Any]:
        """
        Fetches status info for a registered run.
        """
        return self.states.get(w_id, {})

    def clear(self):
        """
        Clears tracker state.
        """
        self.states.clear()
