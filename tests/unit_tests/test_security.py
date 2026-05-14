from app.config.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

def test_hash_password_generates_valid_hash():
    plain_password = "secret123"

    password_hash = hash_password(plain_password)

    assert password_hash != plain_password
    assert verify_password(plain_password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_create_access_token_can_be_decoded():
    access_token = create_access_token("123")

    payload = decode_access_token(access_token)

    assert payload["sub"] == "123"
    assert "exp" in payload