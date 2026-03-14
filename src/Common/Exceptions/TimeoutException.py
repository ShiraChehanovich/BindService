class TimeoutException(Exception):
    message: str = "Timeout occurred while processing the request."
    error_code: int = 408
