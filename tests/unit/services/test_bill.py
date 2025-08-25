"""Unit tests for BillService class."""

import pytest
from unittest.mock import MagicMock
from mpesa_sdk.services.bill import BillService
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient

from mpesa_sdk.bill_manager import (
    BillManagerOptInResponse,
    BillManagerUpdateOptInResponse,
    BillManagerSingleInvoiceResponse,
    BillManagerBulkInvoiceResponse,
    BillManagerCancelInvoiceResponse,
    BillManagerSingleInvoiceRequest,
    InvoiceItem,
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
def bill_service(mock_http_client, mock_token_manager):
    """Fixture to create a BillService instance with mocked dependencies."""
    return BillService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
    )


@pytest.fixture
def bill_service_with_app_key(mock_http_client, mock_token_manager):
    """Fixture to create a BillService instance with mocked dependencies."""
    return BillService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
        app_key="test_app_key",
    )


def test_opt_in_calls_bill_manager_opt_in(bill_service, mock_http_client):
    """Test opt_in calls BillManager.opt_in."""
    response_data = {
        "app_key": "AG_2376487236_126732989KJ",
        "resmsg": "Success",
        "rescode": "200",
    }
    mock_http_client.post.return_value = response_data

    resp = bill_service.opt_in(
        shortcode=123456,
        email="test@example.com",
        official_contact="0712345678",
        send_reminders=1,
        logo=None,
        callback_url="https://callback.url",
    )

    assert isinstance(resp, BillManagerOptInResponse)
    resp.is_successful() is True


def test_bill_manager_update_opt_in(bill_service_with_app_key, mock_http_client):
    """Test update_opt_in calls BillManager.update_opt_in."""
    response_data = {
        "resmsg": "Success",
        "rescode": "200",
    }
    mock_http_client.post.return_value = response_data

    resp = bill_service_with_app_key.update_opt_in(
        shortcode=123456,
        email="update@example.com",
        official_contact="0712345678",
        send_reminders=0,
        logo="logo.png",
        callback_url="https://callback.url",
    )
    assert isinstance(resp, BillManagerUpdateOptInResponse)
    assert resp.is_successful() is True


def test_bill_manager_send_single_invoice(
    bill_service_with_app_key,
    mock_http_client,
):
    """Test send_single_invoice calls BillManager.send_single_invoice."""
    response_data = {
        "Status_Message": "Invoice sent successfully",
        "resmsg": "Success",
        "rescode": "200",
    }
    mock_http_client.post.return_value = response_data

    invoice_items = [MagicMock(spec=InvoiceItem)]

    resp = bill_service_with_app_key.send_single_invoice(
        external_reference="INV123",
        billed_full_name="John Doe",
        billed_phone_number="0712345678",
        billed_period="June 2024",
        invoice_name="June Invoice",
        due_date="2024-06-30",
        account_reference="ACC123",
        amount=1000,
        invoice_items=invoice_items,
    )

    assert isinstance(resp, BillManagerSingleInvoiceResponse)
    assert resp.is_successful() is True


def test_bill_manager_send_bulk_invoice(bill_service_with_app_key, mock_http_client):
    """Test send_bulk_invoice calls BillManager.send_bulk_invoice."""
    response_data = {
        "Status_Message": "Invoice sent successfully",
        "resmsg": "Success",
        "rescode": "200",
    }
    mock_http_client.post.return_value = response_data

    invoices = [MagicMock(spec=BillManagerSingleInvoiceRequest)]

    resp = bill_service_with_app_key.send_bulk_invoice(invoices=invoices)

    assert isinstance(resp, BillManagerBulkInvoiceResponse)
    assert resp.is_successful() is True


def test_bill_manager_cancel_single_invoice(
    bill_service_with_app_key,
    mock_http_client,
):
    """Test cancel_single_invoice calls BillManager.cancel_single_invoice."""
    response_data = {
        "Status_Message": "Invoice cancelled successfully.",
        "resmsg": "Success",
        "rescode": "200",
        "errors": [],
    }

    mock_http_client.post.return_value = response_data
    resp = bill_service_with_app_key.cancel_single_invoice(external_reference="INV123")
    assert isinstance(resp, BillManagerCancelInvoiceResponse)
    assert resp.is_successful() is True


def test_bill_manager_cancel_bulk_invoice(bill_service_with_app_key, mock_http_client):
    """Test cancel_bulk_invoice calls BillManager.cancel_bulk_invoice."""
    response_data = {
        "Status_Message": "Invoices cancelled successfully.",
        "resmsg": "Success",
        "rescode": "200",
        "errors": [],
    }
    mock_http_client.post.return_value = response_data
    resp = bill_service_with_app_key.cancel_bulk_invoice(
        external_references=["INV123", "INV456"]
    )

    assert isinstance(resp, BillManagerCancelInvoiceResponse)
    assert resp.is_successful() is True
