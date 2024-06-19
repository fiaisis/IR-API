import os

import jwt
import requests

AUTH_URL = os.environ.get("AUTH_API_URL", "http://localhost:8001")


def is_token_valid(token: str) -> bool:
    """
    Given a token, check if it signed and not expired via the auth service
    :param token: The token to check
    :return: bool -- True if the token is valid, False otherwise
    """
    response = requests.post(f"http://{AUTH_URL}/api/jwt/checkToken", json={"token": token}, timeout=30)
    return response.text == "ok"


def is_staff(token: str) -> bool:
    """
    Given a token, check if the role is staff. Note this only unpacks the JWT, it does NOT perform signature
    verification. This should be performed separately
    :param token: The token to check
    :return: bool -- True if the role is staff False otherwise
    """
    payload = jwt.decode(token, options={"verify_signature": False})
    return payload.get("role") == "staff"
