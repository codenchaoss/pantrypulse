import logging
import threading
from typing import Dict, Any
from app.llm.provider_registry import ProviderRegistry

logger = logging.getLogger("app.llm")

class HealthMonitor:
    """
    Simulated thread-safe health monitor.
    Periodically checks and records latency/status of active LLM providers.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(HealthMonitor, cls).__new__(cls, *args, **kwargs)
                cls._instance.health_status = {}
                cls._instance.registry = ProviderRegistry()
            return cls._instance

    def check_all_providers(self) -> Dict[str, Any]:
        """
        Runs health check routines across all configured providers.
        """
        with self._lock:
            for priority_idx, name in enumerate(self.registry.priority_order):
                provider = self.registry.get_provider(name)
                priority = priority_idx + 1
                
                if not provider:
                    self.health_status[name] = {
                        "status": "offline",
                        "latency_ms": 0,
                        "priority": priority,
                        "message": "Not implemented"
                    }
                    continue
                
                if not provider.api_key:
                    self.health_status[name] = {
                        "status": "offline",
                        "latency_ms": 0,
                        "priority": priority,
                        "message": "API key is not configured"
                    }
                    continue

                # Run actual check
                check_result = provider.health()
                status = "healthy" if check_result.get("status") == "healthy" else "unhealthy"
                latency = check_result.get("latency_ms", 9999)
                msg = check_result.get("message", "")
                
                self.health_status[name] = {
                    "status": status,
                    "latency_ms": latency,
                    "priority": priority,
                    "message": msg
                }
                
            return self.health_status

    def get_status_report(self) -> Dict[str, Any]:
        """
        Returns the in-memory health report. Runs checks if empty.
        """
        if not self.health_status:
            self.check_all_providers()
        return self.health_status
