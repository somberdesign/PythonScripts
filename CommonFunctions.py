

class Colors:
    OK_GREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m' # No Color

def StringToInt(s:str) -> int:
    """Converts a string to an integer. Returns None if the conversion fails."""
    try:
        return int(s)
    except ValueError:
        return None