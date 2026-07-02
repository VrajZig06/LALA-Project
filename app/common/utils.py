from datetime import datetime, timezone


# Function: Get Unix Time
def get_unix_time() -> int:
    """
    Return UNIX TIME IN MILISECONDS
    """

    return int(datetime.now(tz=timezone.utc).timestamp() * 1000)
