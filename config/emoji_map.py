TOWNHALL_EMOJIS = {
    <:th17:123456789012345694>"
}

def get_townhall_emoji(level: int) -> str:
    """
    Return the custom emoji string for the townhall level.
    If not found, return an empty string.
    """
    return TOWNHALL_EMOJIS.get(level, "")
