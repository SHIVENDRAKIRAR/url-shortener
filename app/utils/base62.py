import random

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def generate_short_code(length: int = 5) -> str:
    return ''.join(random.choices(chars, k=length))