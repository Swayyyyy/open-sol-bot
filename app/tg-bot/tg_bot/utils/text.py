"""Text manipulation utility functions."""


def short_text(text: str, max_length: int = 8) -> str:
    """
    Truncate text to a maximum length and append ellipsis if needed.

    Args:
        text (str): The text to truncate
        max_length (int, optional): Maximum length before truncation. Defaults to 8.

    Returns:
        str: Truncated text with ellipsis if needed
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text
