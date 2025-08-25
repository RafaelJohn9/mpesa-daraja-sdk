"""Unit tests for B2CService class."""

import pytest
from unittest.mock import MagicMock
from mpesa_sdk.services.b2c import B2CService
from mpesa_sdk.B2C import B2CResponse, B2CCommandIDType
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient

from mpesa_sdk.B2C_account_top_up import (
    B2CAccountTopUpResponse,
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
def b2c_service(mock_http_client, mock_token_manager):
    """Fixture to create a B2CService instance with mocked dependencies."""
    return B2CService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
    )


def test_send_payment_calls_b2c_send_payment(b2c_service, mock_http_client):
    """Test that send_payment calls the B2C service."""
    response_data = {
        "OriginatorConversationID": "12345",
        "ConversationID": "AG_20230601_123456789",
        "ResponseCode": "0",
        "ResponseDescription": "Request accepted successfully.",
    }
    mock_http_client.post.return_value = response_data

    resp = b2c_service.send_payment(
        originator_conversation_id="12345-67890-1",
        initiator_name="testapi",
        security_credential="encrypted_credential",
        command_id=B2CCommandIDType.BusinessPayment,
        amount=1000,
        party_a="600999",
        party_b="254712345678",
        remarks="Salary for June",
        queue_timeout_url="https://example.com/timeout",
        result_url="https://example.com/result",
        occasion="JuneSalary",
    )
    assert isinstance(resp, B2CResponse)
    assert resp.ResponseCode == "0"
    assert resp.ResponseDescription == "Request accepted successfully."


def test_account_topup_calls_account_topup(b2c_service, mock_http_client):
    """Test that account_topup calls the B2CAccountTopUp service."""
    response_data = {
        "OriginatorConversationID": "67890",
        "ConversationID": "AG_20230601_987654321",
        "ResponseCode": "0",
        "ResponseDescription": "TopUp accepted successfully.",
    }
    mock_http_client.post.return_value = response_data

    resp = b2c_service.account_topup(
        initiator="apiuser",
        security_credential="secure",
        amount=500,
        party_a="600100",
        party_b="600200",
        account_reference="RefTopUp",
        requester="254711111111",
        remarks="TopUp",
        queue_timeout_url="http://timeout.url",
        result_url="http://result.url",
    )
    assert isinstance(resp, B2CAccountTopUpResponse)
    assert resp.ResponseCode == "0"
    assert resp.ResponseDescription == "TopUp accepted successfully."


def test_send_payment_filters_kwargs(b2c_service, mock_http_client):
    """Test that send_payment filters out unexpected kwargs."""
    response_data = {
        "OriginatorConversationID": "12345",
        "ConversationID": "AG_20230601_123456789",
        "ResponseCode": "0",
        "ResponseDescription": "Request accepted successfully.",
    }
    mock_http_client.post.return_value = response_data

    resp = b2c_service.send_payment(
        originator_conversation_id="12345-67890-1",
        initiator_name="testapi",
        security_credential="encrypted_credential",
        command_id=B2CCommandIDType.BusinessPayment,
        amount=1000,
        party_a="600999",
        party_b="254712345678",
        remarks="Salary for June",
        queue_timeout_url="https://example.com/timeout",
        result_url="https://example.com/result",
        occasion="JuneSalary",
    )
    assert isinstance(resp, B2CResponse)
    assert resp.ResponseCode == "0"
    assert resp.ResponseDescription == "Request accepted successfully."


def test_account_topup_filters_kwargs(b2c_service, mock_http_client):
    """Test that account_topup filters out unexpected kwargs."""
    response_data = {
        "OriginatorConversationID": "67890",
        "ConversationID": "AG_20230601_987654321",
        "ResponseCode": "0",
        "ResponseDescription": "TopUp accepted successfully.",
    }
    mock_http_client.post.return_value = response_data

    resp = b2c_service.account_topup(
        initiator="apiuser",
        security_credential="secure",
        amount=500,
        party_a="600100",
        party_b="600200",
        account_reference="RefTopUp",
        requester="254711111111",
        remarks="TopUp",
        queue_timeout_url="http://timeout.url",
        result_url="http://result.url",
    )
    assert isinstance(resp, B2CAccountTopUpResponse)
    assert resp.ResponseCode == "0"
    assert resp.ResponseDescription == "TopUp accepted successfully."
