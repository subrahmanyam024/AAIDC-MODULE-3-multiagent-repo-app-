from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
import logging

# Configure logger
logger = logging.getLogger(__name__)

def log_retry_attempt(retry_state):
    """Log retry attempts."""
    logger.warning(
        f"Retrying {retry_state.fn.__name__} "
        f"Attempt {retry_state.attempt_number} "
        f"after {retry_state.outcome.exception()}"
    )

# Standard retry configuration for API calls
api_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, TimeoutError)),
    before_sleep=log_retry_attempt,
    reraise=True
)

# Retry configuration for LLM calls (often have rate limits)
llm_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    retry=retry_if_exception_type(Exception), # Broad exception for now, refine for specific LLM errors
    before_sleep=log_retry_attempt,
    reraise=True
)
