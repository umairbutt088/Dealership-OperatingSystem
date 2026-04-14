def norm_plate(plate: str | None) -> str:
    if not plate:
        return ""
    return "".join(c for c in str(plate).upper() if c.isalnum())
