"""Unit tests for the M-Pesa SDK B2C Account TopUp functionality.

This module tests the B2C Account TopUp API client, ensuring it can initiate topup requests,
process responses correctly, and manage callback/error cases.
"""

import pytest
from unittest.mock import MagicMock
from mpesakit.auth import TokenManager
from mpesakit.http_client import HttpClient

from mpesakit.b2c_account_top_up import (
    B2CAccountTopUp,
    B2CAccountTopUpRequest,
    B2CAccountTopUpResponse,
    B2CAccountTopUpCallback,
    B2CAccountTopUpCallbackResponse,
    B2CAccountTopUpTimeoutCallback,
    B2CAccountTopUpTimeoutCallbackResponse,
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
def b2c_account_topup(mock_http_client, mock_token_manager):
    """Fixture to create a B2CAccountTopUp instance with mocked dependencies."""
    return B2CAccountTopUp(
        http_client=mock_http_client, token_manager=mock_token_manager
    )


def valid_b2c_account_topup_request():
    """Create a valid B2CAccountTopUpRequest for testing."""
    return B2CAccountTopUpRequest(
        Initiator="testapi",
        SecurityCredential="secure_credential",
        Amount=239,
        PartyA=600979,
        PartyB=600000,
        AccountReference="353353",
        Requester="254708374149",
        Remarks="OK",
        QueueTimeOutURL="https://mydomain/path/timeout",
        ResultURL="https://mydomain/path/result",
    )


def test_topup_success(b2c_account_topup, mock_http_client):
    """Test that topup request is acknowledged and successful."""
    request = valid_b2c_account_topup_request()
    response_data = {
        "OriginatorConversationID": "5118-111210482-1",
        "ConversationID": "AG_20230420_2010759fd5662ef6d054",
        "ResponseCode": "0",
        "ResponseDescription": "Accept the service request successfully.",
    }
    mock_http_client.post.return_value = response_data

    response = b2c_account_topup.topup(request)

    assert isinstance(response, B2CAccountTopUpResponse)
    assert response.is_successful() is True
    assert response.ResponseCode == response_data["ResponseCode"]
    assert response.ResponseDescription == response_data["ResponseDescription"]


def test_topup_http_error(b2c_account_topup, mock_http_client):
    """Test handling of HTTP errors during topup request."""
    request = valid_b2c_account_topup_request()
    mock_http_client.post.side_effect = Exception("HTTP error")
    with pytest.raises(Exception) as excinfo:
        b2c_account_topup.topup(request)
    assert "HTTP error" in str(excinfo.value)


def test_b2c_account_topup_success_callback():
    """Test parsing of a successful B2C Account TopUp callback."""
    payload = {
        "Result": {
            "ResultType": 0,
            "ResultCode": 0,
            "ResultDesc": "The service request is processed successfully",
            "OriginatorConversationID": "626f6ddf-ab37-4650-b882-b1de92ec9aa4",
            "ConversationID": "12345677dfdf89099B3",
            "TransactionID": "QKA81LK5CY",
            "ResultParameters": {
                "ResultParameter": [
                    {"Key": "Amount", "Value": "190.00"},
                    {"Key": "Currency", "Value": "KES"},
                ]
            },
            "ReferenceData": {
                "ReferenceItem": [
                    {"Key": "BillReferenceNumber", "Value": "19008"},
                ]
            },
        }
    }
    callback = B2CAccountTopUpCallback(**payload)
    assert callback.is_successful() is True
    assert callback.Result.ResultCode == 0
    assert callback.Result.TransactionID == "QKA81LK5CY"
    assert callback.Result.ResultDesc.startswith("The service request is processed")


def test_b2c_account_topup_fail_callback():
    """Test parsing of a failed B2C Account TopUp callback."""
    payload = {
        "Result": {
            "ResultType": 0,
            "ResultCode": 1,
            "ResultDesc": "User cancelled transaction",
            "OriginatorConversationID": "c2a9ba32-9e11-4b90-892c-7bc54944609a",
            "ConversationID": "AG_20230420_2010759fd5662ef6d054",
            "TransactionID": "TX123456",
        }
    }
    callback = B2CAccountTopUpCallback(**payload)
    assert callback.Result.ResultCode == 1
    assert "cancelled" in callback.Result.ResultDesc
    assert callback.Result.TransactionID == "TX123456"


def test_b2c_account_topup_callback_response():
    """Test the response schema for B2C Account TopUp callback."""
    resp = B2CAccountTopUpCallbackResponse()
    assert resp.ResultCode == 0
    assert "processed successfully" in resp.ResultDesc


def test_b2c_account_topup_timeout_callback():
    """Test parsing of a B2C Account TopUp timeout callback."""
    payload = {
        "Result": {
            "ResultType": 1,
            "ResultCode": "1",
            "ResultDesc": "The service request timed out.",
            "OriginatorConversationID": "8521-4298025-1",
            "ConversationID": "AG_20181005_00004d7ee675c0c7ee0b",
        }
    }
    callback = B2CAccountTopUpTimeoutCallback(**payload)
    assert callback.Result.ResultType == 1
    assert callback.Result.ResultCode == "1"
    assert "timed out" in callback.Result.ResultDesc


def test_b2c_account_topup_timeout_callback_response():
    """Test the response schema for B2C Account TopUp timeout callback."""
    resp = B2CAccountTopUpTimeoutCallbackResponse()
    assert resp.ResultCode == 0
    assert "Timeout notification received" in resp.ResultDesc
