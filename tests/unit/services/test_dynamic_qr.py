"""Unit tests for the DynamicQRCodeService class in mpesa_sdk.services.dynamic_qr module."""

import pytest
from unittest.mock import MagicMock
from mpesa_sdk.services.dynamic_qr import DynamicQRCodeService
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.dynamic_qr_code import (
    DynamicQRGenerateResponse,
    DynamicQRTransactionType,
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
def dynamic_qr_service(mock_http_client, mock_token_manager):
    """Creates a DynamicQRCodeService instance for testing."""
    return DynamicQRCodeService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
    )


def test_generate_success(dynamic_qr_service, mock_http_client):
    """Test successful generation of a dynamic QR code."""
    response_data = {
        "ResponseCode": "00",
        "RequestID": "16738-27456357-1",
        "ResponseDescription": "QR Code Successfully Generated.",
        "QRCode": "iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAIAAAD2HxkiAAAHtElEQVR42...",
    }

    mock_http_client.post.return_value = response_data

    resp = dynamic_qr_service.generate(
        merchant_name="Test Merchant",
        ref_no="REF123",
        amount=100.0,
        trx_code=DynamicQRTransactionType.BUY_GOODS,
        cpi="CPI123",
        size="300",
    )
    assert isinstance(resp, DynamicQRGenerateResponse)
    assert resp.is_successful() is True


def test_generate_filters_kwargs(dynamic_qr_service, mock_http_client):
    """Test that extra kwargs are filtered out in the request."""
    response_data = {
        "QRCode": "base64string",
        "MerchantName": "Test Merchant",
        "RefNo": "REF456",
        "Amount": 200.0,
        "TrxCode": DynamicQRTransactionType.BUY_GOODS.value,
        "CPI": "CPI456",
        "Size": "400x400",
        "ResponseCode": "0",
        "ResponseDescription": "QR code generated successfully.",
    }
    mock_http_client.post.return_value = response_data

    resp = dynamic_qr_service.generate(
        merchant_name="Test Merchant",
        ref_no="REF456",
        amount=200.0,
        trx_code=DynamicQRTransactionType.BUY_GOODS.value,
        cpi="CPI456",
        size="400x400",
        ExtraField="should_be_filtered",
    )
    assert isinstance(resp, DynamicQRGenerateResponse)
    assert resp.is_successful() is True


def test_generate_passes_only_model_fields(dynamic_qr_service, mock_http_client):
    """Test that only valid model fields are passed to DynamicQRGenerateRequest."""
    valid_fields = {
        "merchant_name": "Merchant",
        "ref_no": "REF789",
        "amount": 300.0,
        "trx_code": DynamicQRTransactionType.BUY_GOODS.value,
        "cpi": "CPI789",
        "size": "500x500",
    }
    extra_fields = {
        "InvalidField1": "value1",
        "InvalidField2": "value2",
    }
    response_data = {
        "QRCode": "base64string",
        "MerchantName": "Merchant",
        "RefNo": "REF789",
        "Amount": 300.0,
        "TrxCode": "PAY",
        "CPI": "CPI789",
        "Size": "500x500",
        "ResponseCode": "0",
        "ResponseDescription": "QR code generated successfully.",
    }
    mock_http_client.post.return_value = response_data

    resp = dynamic_qr_service.generate(**valid_fields, **extra_fields)
    assert isinstance(resp, DynamicQRGenerateResponse)
    assert resp.is_successful() is True
