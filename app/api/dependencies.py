from fastapi import Request

def get_db(request: Request):
    return request.app.state.db


def parse_expiry_to_seconds(expiry: str) -> int:
    """
    Converts expiry string like '30d', '12h', '3600' to seconds.
    Supports 'd' (days), 'h' (hours), 'm' (minutes), 's' (seconds).
    """
    expiry = expiry.strip().lower()
    if expiry.endswith('d'):
        return int(expiry[:-1]) * 86400
    elif expiry.endswith('h'):
        return int(expiry[:-1]) * 3600
    elif expiry.endswith('m'):
        return int(expiry[:-1]) * 60
    elif expiry.endswith('s'):
        return int(expiry[:-1])
    else:
        # Assume it's seconds if no suffix
        return int(expiry)
