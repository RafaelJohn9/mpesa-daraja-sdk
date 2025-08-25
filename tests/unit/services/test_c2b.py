"""Unit tests for the C2BService class in mpesa_sdk.services.c2b module."""

import pytest
from unittest.mock import MagicMock
from mpesa_sdk.services.c2b import C2BService
from mpesa_sdk.C2B import C2BRegisterUrlResponse, C2BResponseType
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient


@pytest.fixture
def mock_token_manager():
    """Creates a mock TokenManager."""
    mock = MagicMock(spec=TokenManager)
    mock.get_token.return_value = "test_token"
    return mock


@pytest.fixture
def mock_http_client():
    """Creates a mock HttpClient."""
    return MagicMock(spec=HttpClient)


@pytest.fixture
def c2b_service(mock_http_client, mock_token_manager):
    """Creates a C2BService instance for testing."""
    return C2BService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
    )


def test_register_url_success(c2b_service, mock_http_client):
    """Test successful registration of C2B URLs."""
    response_data = {
        "OriginatorConversationID": "12345",
        "ConversationID": "AG_20230601_123456789",
        "ResponseCode": "0",
        "ResponseDescription": "URLs registered successfully.",
    }
    mock_http_client.post.return_value = response_data

    resp = c2b_service.register_url(
        short_code=600999,
        response_type=C2BResponseType.COMPLETED,
        confirmation_url="https://example.com/confirm",
        validation_url="https://example.com/validate",
    )
    assert isinstance(resp, C2BRegisterUrlResponse)
    assert resp.ResponseCode == "0"
    assert resp.ResponseDescription == "URLs registered successfully."


def test_register_url_filters_kwargs(c2b_service, mock_http_client):
    """Test that extra kwargs are filtered out in the request."""
    response_data = {
        "OriginatorConversationID": "67890",
        "ConversationID": "AG_20230601_987654321",
        "ResponseCode": "0",
        "ResponseDescription": "URLs registered successfully.",
    }
    mock_http_client.post.return_value = response_data

    resp = c2b_service.register_url(
        short_code=600999,
        response_type=C2BResponseType.COMPLETED,
        confirmation_url="https://example.com/confirm",
        validation_url="https://example.com/validate",
        ExtraField="should_be_filtered",
    )
    assert isinstance(resp, C2BRegisterUrlResponse)
    assert resp.ResponseCode == "0"
    assert resp.ResponseDescription == "URLs registered successfully."
