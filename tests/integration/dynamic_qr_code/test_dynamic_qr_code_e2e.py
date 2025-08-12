"""End-to-End Test for M-Pesa Dynamic QR Code Generation."""

import os
import pytest
from dotenv import load_dotenv

from mpesa_sdk.dynamic_qr_code import (
    DynamicQRGenerateRequest,
    DynamicQRCode,
    DynamicQRTransactionType,
)
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client.mpesa_http_client import MpesaHttpClient

pytestmark = pytest.mark.live

load_dotenv()


@pytest.fixture
def dynamic_qr_service():
    """Initialize the M-Pesa Dynamic QR Code service with authentication."""
    http_client = MpesaHttpClient(env=os.getenv("MPESA_ENV", "sandbox"))
    token_manager = TokenManager(
        http_client=http_client,
        consumer_key=os.getenv("MPESA_CONSUMER_KEY"),
        consumer_secret=os.getenv("MPESA_CONSUMER_SECRET"),
    )
    return DynamicQRCode(http_client=http_client, token_manager=token_manager)


def test_dynamic_qr_code_generate(dynamic_qr_service):
    """End-to-end test for M-Pesa Dynamic QR Code generation."""
    request = DynamicQRGenerateRequest(
        MerchantName="Test Supermarket",
        RefNo="xewr34fer4t",
        Amount=200,
        TrxCode=DynamicQRTransactionType.BUY_GOODS,
        CPI="373132",
        Size="300",
    )
    response = dynamic_qr_service.generate(request)
    # Basic assertions - adapt as needed for your SDK's response structure
    assert response is not None
    assert hasattr(response, "QRCode") or hasattr(response, "qr_code")
    assert getattr(response, "QRCode", None) or getattr(response, "qr_code", None)
