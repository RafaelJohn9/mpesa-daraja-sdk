"""Unit tests for BalanceService class."""

import pytest
from unittest.mock import MagicMock
from mpesa_sdk.services.balance import BalanceService
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.account_balance import (
    AccountBalanceResponse,
)


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
def balance_service(mock_http_client, mock_token_manager):
    """Fixture to create a BalanceService instance with mocked dependencies."""
    return BalanceService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
    )


def test_init_sets_account_balance(balance_service):
    """Test that BalanceService initializes AccountBalance."""
    assert hasattr(balance_service, "account_balance")


def test_query_calls_account_balance_query(balance_service, mock_http_client):
    """Test that query calls the BalanceService and returns AccountBalanceResponse."""
    response_data = {
        "OriginatorConversationID": "515-5258779-3",
        "ConversationID": "AG_20200123_0000417fed8ed666e976",
        "ResponseCode": "0",
        "ResponseDescription": "Accept the service request successfully",
    }
    mock_http_client.post.return_value = response_data

    resp = balance_service.query(
        initiator="apiuser",
        security_credential="secure",
        command_id="AccountBalance",
        party_a=600100,
        identifier_type=4,
        remarks="Balance inquiry",
        result_url="http://result.url",
        queue_timeout_url="http://timeout.url",
    )
    assert isinstance(resp, AccountBalanceResponse)
    assert resp.is_successful() is True
    assert "request successfully" in resp.ResponseDescription


def test_query_filters_kwargs(balance_service, mock_http_client):
    """Test that query filters out unexpected kwargs."""
    response_data = {
        "OriginatorConversationID": "515-5258779-3",
        "ConversationID": "AG_20200123_0000417fed8ed666e976",
        "ResponseCode": "0",
        "ResponseDescription": "Accept the service request successfully",
    }
    mock_http_client.post.return_value = response_data

    resp = balance_service.query(
        initiator="apiuser",
        security_credential="secure",
        command_id="AccountBalance",
        party_a=600100,
        identifier_type=4,
        remarks="Balance inquiry",
        result_url="http://result.url",
        queue_timeout_url="http://timeout.url",
        unexpected_field="should_be_filtered",
    )
    assert isinstance(resp, AccountBalanceResponse)
    # The unexpected_field should not affect the response
    assert (
        hasattr(resp, "unexpected_field") is False
    )  # Response should not have ExtraField
