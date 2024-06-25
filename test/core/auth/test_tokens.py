"""Test tokens module."""
from http import HTTPStatus
from unittest.mock import Mock, patch

from fia_api.core.auth.tokens import JWTBearer, get_user_from_token

TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"  # noqa: S105
    ".eyJ1c2VybnVtYmVyIjoxMjM0LCJyb2xlIjoidXNlciIsInVzZXJuYW1lIjoiZm9vIiwiZXhwIjoyMTUxMzA1MzA0fQ"
    ".z7qVg2foW61rjYiKXp0Jw_cb5YkbWY-JoNG8GUVo2SY"
)


def test_get_user_from_token():
    """Test user generated form token"""

    user = get_user_from_token(TOKEN)
    expected_user_number = 1234
    assert user.user_number == expected_user_number
    assert user.role == "user"


@patch("fia_api.core.auth.tokens.requests.post")
def test_is_jwt_access_token_valid_valid(mock_post):
    """Test returns true when response is ok"""
    response = Mock()
    response.status_code = HTTPStatus.OK
    mock_post.return_value = response

    jwtbearer = JWTBearer()
    assert jwtbearer._is_jwt_access_token_valid(TOKEN)


@patch("fia_api.core.auth.tokens.requests.post")
def test_is_jwt_access_token_valid_invalid(mock_post):
    """Test returns False when response is forbidden"""
    response = Mock()
    response.status_code = HTTPStatus.FORBIDDEN
    mock_post.return_value = response

    jwtbearer = JWTBearer()
    assert not jwtbearer._is_jwt_access_token_valid(TOKEN)


@patch("fia_api.core.auth.tokens.requests.post")
def test_is_jwt_access_token_valid_raises_returns_invalid(mock_post):
    """Test returns False is verification fails"""
    mock_post.side_effect = RuntimeError

    jwtbearer = JWTBearer()
    assert not jwtbearer._is_jwt_access_token_valid(TOKEN)
