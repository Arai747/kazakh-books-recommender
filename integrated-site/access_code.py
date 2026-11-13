
"""BookRec пайдаланушыларына арналған жеке кіру кодтары."""

import re
import secrets


def generate_access_code():
    """Криптографиялық кездейсоқ 32 таңбалы код жасау."""
    return secrets.token_hex(16)


def validate_access_code(code):
    """Кодтың дұрыс форматта екенін тексеру."""
    if not isinstance(code, str):
        return False

    return bool(re.fullmatch(r"[0-9a-f]{32}", code.strip().lower()))


def normalize_access_code(code):
    """Кодты бірдей форматқа келтіру."""
    if not validate_access_code(code):
        raise ValueError("Жеке код 32 таңбалы болуы керек.")

    return code.strip().lower()
