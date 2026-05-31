MAX_BUFFER_MINUTES = 480


def effective_buffer_minutes(value) -> int:
    try:
        minutes = int(value or 0)
    except (TypeError, ValueError):
        return 0
    return max(0, min(minutes, MAX_BUFFER_MINUTES))
