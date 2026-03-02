import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger("quote_automation")

# Standard retry: 3 attempts, exponential backoff 2s -> 4s -> 8s
api_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((
        ConnectionError,
        TimeoutError,
        Exception,  # Catch broad exceptions from API libraries
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
