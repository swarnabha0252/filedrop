import secrets
import string
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()


def generate_secure_token(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_delete_token() -> str:
    return generate_secure_token(32)


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False


def hash_delete_token(token: str) -> str:
    return ph.hash(token)


def verify_delete_token(token: str, token_hash: str) -> bool:
    try:
        ph.verify(token_hash, token)
        return True
    except VerifyMismatchError:
        return False