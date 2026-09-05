from app.core.security import generate_secure_token, generate_delete_token
from app.core.config import settings


def generate_public_token() -> str:
    return generate_secure_token(settings.TOKEN_LENGTH)


def generate_private_delete_token() -> str:
    return generate_delete_token()