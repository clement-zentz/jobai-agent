# app/utils/truncate_string.py


def shorten_text(text: str, max_length: int = 30) -> str:
    """Shorten a string to appoximately `max_length` characters
    without cutting words. If the string is shorter, return it as-is.
    """
    text = text.strip()

    # If already small enough, return directly
    if len(text) <= max_length:
        return text
    
    # Find the last space before max_length
    cut_index = text.rfind(" ", 0, max_length)

    # If no space found, fall back to hard cut
    if cut_index == -1:
        return text[:max_length].rstrip() + "..."
    
    return text[:cut_index].rstrip() + "..."