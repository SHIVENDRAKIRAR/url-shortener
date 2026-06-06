chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
BASE = 62


def encode(num):
    if num == 0:
        return "a"

    result = ""

    while num > 0:
        rem = num % BASE
        result += chars[rem]
        num = num // BASE

    return result[::-1]