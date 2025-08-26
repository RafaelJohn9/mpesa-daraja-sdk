"""Unit tests for ReversalService class."""

import pytest
from unittest.mock import MagicMock
from mpesa_sdk.services.reversal import ReversalService
from mpesa_sdk.reversal import ReversalResponse
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient


@pytest.fixture
def mock_token_manager():
    """Mock TokenManager to return a fixed token."""
    mock = MagicMock(spec=TokenManager)
    mock.get_token.return_value = "test_token"
    return mock


@pytest.fixture
def mock_http_client():
    """Mock HttpClient to simulate HTTP requests."""
    return MagicMock(spec=HttpClient)


@pytest.fixture
def reversal_service(mock_http_client, mock_token_manager):
    """Fixture to create a ReversalService instance with mocked dependencies."""
    return ReversalService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
    )


def test_reverse_calls_reversal(reversal_service, mock_http_client):
    """Test that reverse calls the Reversal.reverse method with correct request."""
    response_data = {
        "OriginatorConversationID": "71840-27539181-07",
        "ConversationID": "AG_20210709_12346c8e6f8858d7b70a",
        "ResponseCode": "0",
        "ResponseDescription": "Accept the service request successfully.",
    }
    mock_http_client.post.return_value = response_data

    resp = reversal_service.reverse(
        initiator="TestInit610",
        security_credential="encrypted_credential",
        transaction_id="LKXXXX1234",
        amount=100,
        receiver_party=600610,
        result_url="https://ip:port/result",
        queue_timeout_url="https://ip:port/timeout",
        remarks="Test",
        occasion="work",
    )
    assert isinstance(resp, ReversalResponse)
    assert resp.is_successful() is True
    assert resp.ResponseDescription == "Accept the service request successfully."


def test_reverse_filters_kwargs(reversal_service, mock_http_client):
    """Test that reverse filters out unexpected kwargs."""
    response_data = {
        "OriginatorConversationID": "71840-27539181-07",
        "ConversationID": "AG_20210709_12346c8e6f8858d7b70a",
        "ResponseCode": "0",
        "ResponseDescription": "Accept the service request successfully.",
    }
    mock_http_client.post.return_value = response_data

    resp = reversal_service.reverse(
        initiator="TestInit610",
        security_credential="encrypted_credential",
        transaction_id="LKXXXX1234",
        amount=100,
        receiver_party=600610,
        result_url="https://ip:port/result",
        queue_timeout_url="https://ip:port/timeout",
        remarks="Test",
        occasion="work",
        unexpected_field="should be ignored",
    )
    assert isinstance(resp, ReversalResponse)
    assert resp.is_successful() is True

    # unexpected_field should not be present
    assert not hasattr(resp, "unexpected_field")


def test_reversal_service_initializes_reversal_correctly(
    mock_http_client, mock_token_manager
):
    """Test ReversalService initializes Reversal with correct arguments."""
    service = ReversalService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
    )
    assert service.http_client is mock_http_client
    assert service.token_manager is mock_token_manager
    # If ReversalService has an internal 'reversal' attribute, check its dependencies
    if hasattr(service, "reversal"):
        assert service.reversal.http_client is mock_http_client
        assert service.reversal.token_manager is mock_token_manager
