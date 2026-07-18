import time
import logging
from typing import Callable, Any, Dict

logger = logging.getLogger("app.llm")

class RetryManager:
    """
    Handles API execution retries using exponential backoff.
    """
    @staticmethod
    def execute_with_retry(
        func: Callable[[], Dict[str, Any]], 
        max_retries: int = 2, 
        base_delay_sec: float = 1.0
    ) -> Dict[str, Any]:
        """
        Executes a generator function and retries if it returns a transient error.
        Only retries for rate limits (HTTP 429), timeouts, and internal server errors (500+).
        """
        last_result = {"status": "error", "text": "", "error": "No execution attempt was made."}
        
        for attempt in range(1 + max_retries):
            attempt_num = attempt + 1
            try:
                res = func()
                if res.get("status") == "success":
                    return res
                
                last_result = res
                err_msg = res.get("error", "")
                
                # Identify if error is retryable
                is_retryable = False
                if "429" in err_msg or "rate limit" in err_msg.lower() or "quota" in err_msg.lower():
                    is_retryable = True
                elif "timeout" in err_msg.lower():
                    is_retryable = True
                elif any(f"HTTP {code}" in err_msg for code in ["500", "502", "503", "504"]):
                    is_retryable = True
                
                # Check for bad key errors (don't retry authentication failures)
                if any(f"HTTP {code}" in err_msg for code in ["401", "403"]) or "api key" in err_msg.lower():
                    is_retryable = False
                
                if not is_retryable or attempt == max_retries:
                    break
                    
                delay = base_delay_sec * (2 ** attempt)
                logger.warning(
                    f"RetryManager: Request failed with retryable error. "
                    f"Retrying in {delay:.2f}s... (Attempt {attempt_num}/{1 + max_retries})"
                )
                time.sleep(delay)
                
            except Exception as e:
                err_msg = str(e)
                last_result = {"status": "error", "text": "", "error": err_msg}
                if attempt == max_retries:
                    break
                
                delay = base_delay_sec * (2 ** attempt)
                logger.warning(
                    f"RetryManager: Exception encountered: {err_msg}. "
                    f"Retrying in {delay:.2f}s... (Attempt {attempt_num}/{1 + max_retries})"
                )
                time.sleep(delay)
                
        return last_result
