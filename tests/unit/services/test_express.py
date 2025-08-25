"""Unit tests for the StkPushService facade in mpesa_sdk.services.express module."""

import pytest
from unittest.mock import MagicMock
from mpesa_sdk.services.express import StkPushService
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient

from mpesa_sdk.mpesa_express import (
    StkPushSimulateResponse,
    StkPushQueryResponse,
    TransactionType,
)


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
def stk_push_service(mock_http_client, mock_token_manager):
    """Creates a StkPushService instance for testing."""
    # Patch StkPush inside the service to use a mock
    service = StkPushService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
    )
    return service


def test_push_success(stk_push_service, mock_http_client):
    """Test successful STK Push transaction."""
    response = {
        "MerchantRequestID": "16813-1590513-1",
        "CheckoutRequestID": "ws_CO_DMZ_123212312_2342347678234",
        "ResponseCode": 0,
        "ResponseDescription": "Accepted",
        "CustomerMessage": "Success. Request accepted for processing.",
    }
    mock_http_client.post.return_value = response

    resp = stk_push_service.push(
        business_short_code=654321,
        passkey="testpasskey",
        transaction_type=TransactionType.CUSTOMER_PAYBILL_ONLINE.value,
        amount=10,
        party_a="254712345678",
        party_b="654321",
        phone_number="254712345678",
        callback_url="https://example.com/callback",
        account_reference="Test",
        transaction_desc="Payment",
    )

    assert isinstance(resp, StkPushSimulateResponse)
    assert resp.is_successful() is True


def test_push_filters_kwargs(stk_push_service, mock_http_client):
    """Test that extra kwargs are filtered out in push."""
    response = {
        "MerchantRequestID": "16813-1590513-1",
        "CheckoutRequestID": "ws_CO_DMZ_123212312_2342347678234",
        "ResponseCode": 0,
        "ResponseDescription": "Accepted",
        "CustomerMessage": "Success. Request accepted for processing.",
    }

    mock_http_client.post.return_value = response

    resp = stk_push_service.push(
        business_short_code=654321,
        passkey="testpasskey",
        transaction_type=TransactionType.CUSTOMER_PAYBILL_ONLINE.value,
        amount=10,
        party_a="254712345678",
        party_b="654321",
        phone_number="254712345678",
        callback_url="https://example.com/callback",
        account_reference="Test",
        transaction_desc="Payment",
        ExtraField="should_be_filtered",
    )
    assert isinstance(resp, StkPushSimulateResponse)
    assert not hasattr(resp, "ExtraField")


def test_query_success(stk_push_service, mock_http_client):
    """Test successful STK Push query."""
    response = {
        "MerchantRequestID": "22205-34066-1",
        "CheckoutRequestID": "ws_CO_13012021093521236557",
        "ResponseCode": 0,
        "ResponseDescription": "Accepted",
        "ResultCode": 0,
        "ResultDesc": "Processed successfully.",
    }
    mock_http_client.post.return_value = response

    resp = stk_push_service.query(
        business_short_code=654321,
        passkey="testpasskey",
        checkout_request_id="ws_CO_13012021093521236557",
    )
    assert isinstance(resp, StkPushQueryResponse)
    assert resp.is_successful() is True


def test_query_filters_kwargs(stk_push_service, mock_http_client):
    """Test that extra kwargs are filtered out in query."""
    response = {
        "MerchantRequestID": "22205-34066-1",
        "CheckoutRequestID": "ws_CO_13012021093521236557",
        "ResponseCode": 0,
        "ResponseDescription": "Accepted",
        "ResultCode": 0,
        "ResultDesc": "Processed successfully.",
    }
    mock_http_client.post.return_value = response

    resp = stk_push_service.query(
        business_short_code=654321,
        passkey="testpasskey",
        checkout_request_id="ws_CO_13012021093521236557",
        ExtraField="should_be_filtered",
    )
    assert isinstance(resp, StkPushQueryResponse)
    resp.is_successful() is True
    assert not hasattr(resp, "ExtraField")
