"""Unit tests for MpesaClient and its services."""

import pytest
from mpesa_sdk.mpesa_client import MpesaClient
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import MpesaHttpClient

from mpesa_sdk.services import (
    B2BService,
    B2CService,
    BalanceService,
    BillService,
    C2BService,
    DynamicQRCodeService,
    StkPushService,
    RatibaService,
    ReversalService,
    TaxService,
    TransactionService,
)


@pytest.fixture
def client():
    """Creates a MpesaClient instance for testing."""
    return MpesaClient("dummy_key", "dummy_secret")


def test_http_client_instance(client):
    """Test that the http_client is an instance of MpesaHttpClient."""
    assert isinstance(client.http_client, MpesaHttpClient)


def test_token_manager_instance(client):
    """Test that the token_manager is an instance of TokenManager."""
    assert isinstance(client.token_manager, TokenManager)


def test_express_service_instance(client):
    """Test that the express service is an instance of StkPushService."""
    assert isinstance(client.express, StkPushService)


def test_b2c_service_instance(client):
    """Test that the b2c service is an instance of B2CService."""
    assert isinstance(client.b2c, B2CService)


def test_b2b_service_instance(client):
    """Test that the b2b service is an instance of B2BService."""
    assert isinstance(client.b2b, B2BService)


def test_transactions_service_instance(client):
    """Test that the transactions service is an instance of TransactionService."""
    assert isinstance(client.transactions, TransactionService)


def test_tax_service_instance(client):
    """Test that the tax service is an instance of TaxService."""
    assert isinstance(client.tax, TaxService)


def test_balance_service_instance(client):
    """Test that the balance service is an instance of BalanceService."""
    assert isinstance(client.balance, BalanceService)


def test_reversal_service_instance(client):
    """Test that the reversal service is an instance of ReversalService."""
    assert isinstance(client.reversal, ReversalService)


def test_bill_service_instance(client):
    """Test that the bill service is an instance of BillService."""
    assert isinstance(client.bill, BillService)


def test_dynamic_qr_service_instance(client):
    """Test that the dynamic QR service is an instance of DynamicQRCodeService."""
    assert isinstance(client.dynamic_qr, DynamicQRCodeService)


def test_c2b_service_instance(client):
    """Test that the c2b service is an instance of C2BService."""
    assert isinstance(client.c2b, C2BService)


def test_ratiba_service_instance(client):
    """Test that the ratiba service is an instance of RatibaService."""
    assert isinstance(client.ratiba, RatibaService)
