"""Unit tests for the STK Push functionality of the Mpesa SDK.

This module tests the StkPush class for initiating and querying M-Pesa STK Push transactions.
"""

import pytest
from unittest.mock import MagicMock
from mpesakit.mpesa_express.stk_push import (
    StkPush,
    StkPushSimulateRequest,
    StkPushSimulateResponse,
    StkPushQueryRequest,
    StkPushQueryResponse,
)
from mpesakit.auth import TokenManager
from mpesakit.http_client import HttpClient


@pytest.fixture
def mock_token_manager():
    """Mock TokenManager to return a fixed token for testing."""
    mock = MagicMock(spec=TokenManager)
    mock.get_token.return_value = "test_token"
    return mock


@pytest.fixture
def mock_http_client():
    """Mock HttpClient for testing."""
    return MagicMock(spec=HttpClient)


@pytest.fixture
def stk_push(mock_http_client, mock_token_manager):
    """Fixture to create an instance of StkPush with mocked dependencies."""
    return StkPush(http_client=mock_http_client, token_manager=mock_token_manager)


def test_push_success(stk_push, mock_http_client):
    """Test that a successful STK Push transaction can be initiated."""
    request = StkPushSimulateRequest(
        BusinessShortCode=174379,
        Password="test_password",
        Timestamp="20220101010101",
        TransactionType="CustomerPayBillOnline",
        Amount=10,
        PartyA="254700000000",
        PartyB="174379",
        PhoneNumber="254700000000",
        CallBackURL="https://test.com/callback",
        AccountReference="TestAccount",
        TransactionDesc="Test Payment",
    )
    response_data = {
        "MerchantRequestID": "12345",
        "CheckoutRequestID": "67890",
        "ResponseCode": 0,
        "ResponseDescription": "Success",
        "CustomerMessage": "Success",
    }
    mock_http_client.post.return_value = response_data

    response = stk_push.push(request)

    assert isinstance(response, StkPushSimulateResponse)
    assert response.MerchantRequestID == "12345"
    assert response.is_successful() is True
    mock_http_client.post.assert_called_once()
    args, kwargs = mock_http_client.post.call_args
    assert args[0] == "/mpesa/stkpush/v1/processrequest"
    assert kwargs["headers"]["Authorization"] == "Bearer test_token"


def test_query_success(stk_push, mock_http_client):
    """Test that the status of an STK Push transaction can be queried successfully."""
    request = StkPushQueryRequest(
        BusinessShortCode=174379,
        Password="test_password",
        Timestamp="20220101010101",
        CheckoutRequestID="ws_CO_260520211133524545",
    )
    response_data = {
        "MerchantRequestID": "12345",
        "CheckoutRequestID": "ws_CO_260520211133524545",
        "ResponseCode": 0,
        "ResponseDescription": "Success",
        "ResultCode": 0,
        "ResultDesc": "The service request is processed successfully.",
    }
    mock_http_client.post.return_value = response_data

    response = stk_push.query(request)

    assert isinstance(response, StkPushQueryResponse)
    assert response.is_successful() is True
    assert response.CheckoutRequestID == "ws_CO_260520211133524545"
    mock_http_client.post.assert_called_once()
    args, kwargs = mock_http_client.post.call_args
    assert args[0] == "/mpesa/stkpushquery/v1/query"
    assert kwargs["headers"]["Authorization"] == "Bearer test_token"


def test_push_handles_http_error(stk_push, mock_http_client):
    """Test that an HTTP error during STK Push initiation is handled."""
    request = StkPushSimulateRequest(
        BusinessShortCode=174379,
        Password="test_password",
        Timestamp="20220101010101",
        TransactionType="CustomerPayBillOnline",
        Amount=10,
        PartyA="254700000000",
        PartyB="174379",
        PhoneNumber="254700000000",
        CallBackURL="https://test.com/callback",
        AccountReference="TestAccount",
        TransactionDesc="Test Payment",
    )
    mock_http_client.post.side_effect = Exception("HTTP error")

    with pytest.raises(Exception) as excinfo:
        stk_push.push(request)
    assert "HTTP error" in str(excinfo.value)


def test_query_handles_http_error(stk_push, mock_http_client):
    """Test that an HTTP error during STK Push query is handled."""
    request = StkPushQueryRequest(
        BusinessShortCode=174379,
        Password="test_password",
        Timestamp="20220101010101",
        CheckoutRequestID="67890",
    )
    mock_http_client.post.side_effect = Exception("HTTP error")

    with pytest.raises(Exception) as excinfo:
        stk_push.query(request)
    assert "HTTP error" in str(excinfo.value)


def test_stk_push_simulate_request_invalid_transaction_type():
    """Test that StkPushSimulateRequest raises ValueError for invalid TransactionType."""
    invalid_transaction_type = "InvalidType"
    valid_kwargs = dict(
        BusinessShortCode=174379,
        Password="test_password",
        Timestamp="20220101010101",
        TransactionType=invalid_transaction_type,
        Amount=10,
        PartyA="254700000000",
        PartyB="174379",
        PhoneNumber="254700000000",
        CallBackURL="https://test.com/callback",
        AccountReference="TestAccount",
        TransactionDesc="Test Payment",
    )
    with pytest.raises(ValueError) as excinfo:
        StkPushSimulateRequest(**valid_kwargs)
    assert "TransactionType must be one of:" in str(excinfo.value)
