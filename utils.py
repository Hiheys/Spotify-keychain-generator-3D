def get_link_data(link: str):
    """
    Parse a Spotify share link and return (type, id) tuple.

    Supports formats:
    - https://open.spotify.com/track/4R1bPIiMEr5xfejy05H7cW
    - https://open.spotify.com/intl-pl/track/4R1bPIiMEr5xfejy05H7cW?si=...
    - spotify:track:4R1bPIiMEr5xfejy05H7cW

    Returns tuple (type, id) or None on failure.
    """
    VALID_TYPES = {"track", "album", "artist", "playlist"}

    link = link.strip()

    # Handle spotify URI format: spotify:track:ID
    if link.startswith("spotify:"):
        parts = link.split(":")
        if len(parts) == 3 and parts[1] in VALID_TYPES:
            return (parts[1], parts[2])
        return None

    # Handle URL format — strip query params first
    link = link.split("?")[0].split("#")[0]
    parts = link.split("/")

    for i, part in enumerate(parts):
        if part in VALID_TYPES:
            if i + 1 < len(parts) and parts[i + 1]:
                return (part, parts[i + 1])

    return None
