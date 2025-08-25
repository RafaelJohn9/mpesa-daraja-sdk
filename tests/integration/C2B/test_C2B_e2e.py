"""End-to-End Test for M-Pesa C2B Register URL, Validation, and Confirmation.

This test simulates registering C2B URLs

We haven't been able to test the validation and confirmation endpoints in the sandbox environment
and ensures that the M-Pesa C2B service works end-to-end.
"""

# TODO: When available, test the validation and confirmation endpoints in the sandbox environment.

import os
import pytest
from dotenv import load_dotenv

from mpesa_sdk.C2B.C2B import C2B
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import MpesaHttpClient
from mpesa_sdk.C2B import (
    C2BRegisterUrlRequest,
)

load_dotenv()
pytestmark = pytest.mark.live


@pytest.fixture
def c2b_service():
    """Initialize the M-Pesa C2B service with authentication."""
    http_client = MpesaHttpClient(env=os.getenv("MPESA_ENV", "sandbox"))
    token_manager = TokenManager(
        consumer_key=os.getenv("MPESA_CONSUMER_KEY"),
        consumer_secret=os.getenv("MPESA_CONSUMER_SECRET"),
        http_client=http_client,
    )
    return C2B(http_client=http_client, token_manager=token_manager)


def test_c2b_register_url_e2e(c2b_service):
    """End-to-end test for M-Pesa C2B Register URL, Validation, and Confirmation."""
    print("🔗 Starting E2E Test: C2B Register URL, Validation, and Confirmation")

    validation_url = "https://domainpath.com/c2b/validation"
    confirmation_url = "https://domainpath.com/c2b/confirmation"
    print(f"📨 Using validation URL: {validation_url}")
    print(f"📨 Using confirmation URL: {confirmation_url}")

    # 1. Register URLs
    register_request = C2BRegisterUrlRequest(
        ShortCode=600997,
        ResponseType="Completed",
        ConfirmationURL=confirmation_url,
        ValidationURL=validation_url,
    )
    print(f"📤 Registering URLs with request: {dict(register_request)}")
    response = c2b_service.register_url(request=register_request)
    print(f"✅ Register URL response: {response}")

    assert response.ResponseDescription is not None
    assert response.OriginatorConversationID is not None
