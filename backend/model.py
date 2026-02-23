
def append_suffix(user_text: str, suffix: str = " — processed") -> str:
    user_text = (user_text or "").strip()
    if not user_text:
        return "THis text was added by the backend."
    return f"{user_text}{suffix}"
