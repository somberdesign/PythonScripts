

def StringToInt(s:str) -> int:
    """Converts a string to an integer. Returns None if the conversion fails."""
    try:
        return int(s)
    except ValueError:
        return None