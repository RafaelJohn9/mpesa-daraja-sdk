"""Unit tests for the TokenManager class in the mpesa_sdk.auth module.

These tests cover token retrieval, caching, and error handling.
"""

import pytest
from unittest.mock import MagicMock
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.errors import MpesaApiException, MpesaError


@pytest.fixture
def valid_credentials():
    """Provide valid M-Pesa credentials for testing."""
    return {
        "consumer_key": "test_key",
        "consumer_secret": "test_secret",
    }


@pytest.fixture
def invalid_credentials():
    """Provide invalid M-Pesa credentials for testing."""
    return {
        "consumer_key": "invalid_key",
        "consumer_secret": "invalid_secret",
    }


@pytest.fixture
def mock_http_client():
    """Provide a MagicMock HttpClient for testing."""
    client = MagicMock(spec=HttpClient)
    return client


def test_get_token_success(valid_credentials, mock_http_client):
    """Test that a valid token can be retrieved."""
    mock_http_client.get.return_value = {
        "access_token": "mocked_token_1234567890",
        "expires_in": 3600,
    }
    tm = TokenManager(
        consumer_key=valid_credentials["consumer_key"],
        consumer_secret=valid_credentials["consumer_secret"],
        http_client=mock_http_client,
    )
    token = tm.get_token()
    assert token == "mocked_token_1234567890"


def test_token_caching(valid_credentials, mock_http_client):
    """Test that the token is cached and reused until it expires."""
    mock_http_client.get.return_value = {
        "access_token": "cached_token_1234567890",
        "expires_in": 3600,
    }
    tm = TokenManager(
        consumer_key=valid_credentials["consumer_key"],
        consumer_secret=valid_credentials["consumer_secret"],
        http_client=mock_http_client,
    )
    token1 = tm.get_token()
    token2 = tm.get_token()
    assert token1 == token2


def test_force_refresh_token(valid_credentials, mock_http_client):
    """Test that forcing a token refresh retrieves a new token."""
    mock_http_client.get.side_effect = [
        {"access_token": "token1", "expires_in": 3600},
        {"access_token": "token2", "expires_in": 3600},
    ]
    tm = TokenManager(
        consumer_key=valid_credentials["consumer_key"],
        consumer_secret=valid_credentials["consumer_secret"],
        http_client=mock_http_client,
    )
    token1 = tm.get_token()
    token2 = tm.get_token(force_refresh=True)
    assert token1 == "token1"
    assert token2 == "token2"


def test_invalid_credentials_raises(mock_http_client, invalid_credentials):
    """Test that invalid credentials raise an exception."""
    mock_http_client.get.side_effect = MpesaApiException(
        MpesaError(
            error_code="AUTH_INVALID_CREDENTIALS",
            error_message="Invalid credentials",
            status_code=403,
        )
    )
    tm = TokenManager(
        consumer_key=invalid_credentials["consumer_key"],
        consumer_secret=invalid_credentials["consumer_secret"],
        http_client=mock_http_client,
    )
    with pytest.raises(MpesaApiException) as excinfo:
        tm.get_token()
    assert (
        "Invalid credentials" in str(excinfo.value)
        or excinfo.value.error.status_code == 403
    )


def test_invalid_grant_type(valid_credentials, mock_http_client, monkeypatch):
    """Test that an invalid grant type raises an exception."""
    tm = TokenManager(
        consumer_key=valid_credentials["consumer_key"],
        consumer_secret=valid_credentials["consumer_secret"],
        http_client=mock_http_client,
    )
    mock_http_client.get.side_effect = MpesaApiException(
        MpesaError(
            error_code="AUTH_INVALID_GRANT_TYPE",
            error_message="Invalid grant_type",
            status_code=403,
        )
    )
    with pytest.raises(MpesaApiException) as excinfo:
        tm.get_token(force_refresh=True)
    assert excinfo.value.error.status_code == 403


def test_invalid_auth_type(valid_credentials, mock_http_client, monkeypatch):
    """Test that an invalid auth type raises an exception."""
    tm = TokenManager(
        consumer_key=valid_credentials["consumer_key"],
        consumer_secret=valid_credentials["consumer_secret"],
        http_client=mock_http_client,
    )
    monkeypatch.setattr(tm, "_get_basic_auth_header", lambda: "Bearer something")
    mock_http_client.get.side_effect = MpesaApiException(
        MpesaError(
            error_code="AUTH_INVALID_AUTH_TYPE",
            error_message="Invalid auth type",
            status_code=403,
        )
    )
    with pytest.raises(MpesaApiException) as excinfo:
        tm.get_token(force_refresh=True)
    assert excinfo.value.error.status_code == 403


def test_mpesa_api_exception_with_empty_error_message(
    valid_credentials, mock_http_client, monkeypatch
):
    """Test that an empty error message raises a specific exception."""
    tm = TokenManager(
        consumer_key=valid_credentials["consumer_key"],
        consumer_secret=valid_credentials["consumer_secret"],
        http_client=mock_http_client,
    )

    def fake_get(*args, **kwargs):
        raise MpesaApiException(
            MpesaError(
                error_code="SOME_CODE",
                error_message="",
                status_code=400,
            )
        )

    monkeypatch.setattr(mock_http_client, "get", fake_get)
    with pytest.raises(MpesaApiException) as excinfo:
        tm.get_token(force_refresh=True)
    err = excinfo.value.error
    assert err.error_code == "AUTH_INVALID_CREDENTIALS"
    assert "Invalid credentials" in err.error_message
    assert err.status_code == 400


def test_token_missing_raises_exception(
    valid_credentials, mock_http_client, monkeypatch
):
    """Test that a missing token raises an exception."""
    tm = TokenManager(
        consumer_key=valid_credentials["consumer_key"],
        consumer_secret=valid_credentials["consumer_secret"],
        http_client=mock_http_client,
    )

    def fake_get(*args, **kwargs):
        return {"expires_in": 3600}

    monkeypatch.setattr(mock_http_client, "get", fake_get)
    with pytest.raises(MpesaApiException) as excinfo:
        tm.get_token(force_refresh=True)
    err = excinfo.value.error
    assert err.error_code == "TOKEN_MISSING"
    assert "No access token returned" in err.error_message
    assert err.raw_response == {"expires_in": 3600}
