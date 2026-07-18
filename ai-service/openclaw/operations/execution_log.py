from datetime import datetime, timezone
import threading
from typing import Dict, Any, List

class ExecutionLogger:
    """
    Simulated in-memory thread-safe execution log recorder.
    Records timings and logs generated during workflow execution.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ExecutionLogger, cls).__new__(cls, *args, **kwargs)
                cls._instance.logs = {}
            return cls._instance

    def initialize_log(self, w_id: str):
        """
        Creates an execution log container.
        """
        self.logs[w_id] = {
            "workflow_id": w_id,
            "duration_ms": 0,
            "steps": [],
            "completed_skills": [],
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    def log_step(self, w_id: str, skill_name: str, duration_ms: float, status: str, warnings: List[str] = None):
        """
        Records details for a skill trigger step.
        """
        if w_id in self.logs:
            self.logs[w_id]["steps"].append({
                "skill": skill_name,
                "duration_ms": int(duration_ms),
                "status": status,
                "warnings": warnings or [],
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            })
            if status == "success":
                self.logs[w_id]["completed_skills"].append(skill_name)

    def finalize_log(self, w_id: str, total_duration_ms: float):
        """
        Sets overall run duration.
        """
        if w_id in self.logs:
            self.logs[w_id]["duration_ms"] = int(total_duration_ms)

    def get_log(self, w_id: str) -> Dict[str, Any]:
        """
        Gets log file details.
        """
        return self.logs.get(w_id, {})

    def clear(self):
        """
        Clears logger state.
        """
        self.logs.clear()
