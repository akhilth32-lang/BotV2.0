TOWNHALL_EMOJIS = {
    17:"<:emoji_63:1309505639025741875>"
}

def get_townhall_emoji(level: int) -> str:
    """
    Return the custom emoji string for the townhall level.
    If not found, return an empty string.
    """
    return TOWNHALL_EMOJIS.get(level, "")
