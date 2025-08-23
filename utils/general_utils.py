# utils/general_utils.py

import re

def normalize_player_tag(tag: str) -> str:
    """Normalize player tag by removing spaces and replacing 'O' with '0' if needed."""
    tag = tag.strip().upper()
    tag = tag.replace(' ', '')
    tag = tag.replace('O', '0')
    return tag

def is_valid_player_tag(tag: str) -> bool:
    """Return True if player tag matches valid Clash of Clans tag format."""
    # Clash tags must start with ‘#’ and contain 3-9 chars (0-9, A-Z, and special chars)
    pattern = r'^#?[0289PYLQGRJCUV]{3,9}$'
    return bool(re.match(pattern, tag))

def paginate_list(items: list, page: int, page_size: int) -> list:
    """Return a slice of the list for the given page and size."""
    if page < 1:
        page = 1
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]

def format_trophy_change(change: int) -> str:
    """Format trophy change with sign."""
    return f"{change:+d}"

