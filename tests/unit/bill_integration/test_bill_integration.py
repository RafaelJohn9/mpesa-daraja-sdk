"""Unit tests for the M-Pesa SDK Bill Manager functionality.

This module tests the Bill Manager API client, ensuring it can handle onboarding,
invoicing, cancellation, and error cases.
"""

import pytest
from unittest.mock import MagicMock
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.bill_manager.bill_manager import BillManager
from datetime import datetime
from pydantic import ValidationError

from mpesa_sdk.bill_manager.schemas import (
    BillManagerOptInRequest,
    BillManagerOptInResponse,
    BillManagerUpdateOptInRequest,
    BillManagerUpdateOptInResponse,
    BillManagerSingleInvoiceRequest,
    BillManagerSingleInvoiceResponse,
    BillManagerBulkInvoiceRequest,
    BillManagerBulkInvoiceResponse,
    BillManagerCancelSingleInvoiceRequest,
    BillManagerCancelBulkInvoiceRequest,
    BillManagerCancelInvoiceResponse,
)


@pytest.fixture
def mock_token_manager():
    """Mock TokenManager for testing purposes."""
    mock = MagicMock(spec=TokenManager)
    mock.get_token.return_value = "test_token"
    return mock


@pytest.fixture
def mock_http_client():
    """Mock HttpClient for testing purposes."""
    return MagicMock(spec=HttpClient)


@pytest.fixture
def bill_manager(mock_http_client, mock_token_manager):
    """Fixture to create a BillManager instance with mocked HttpClient and TokenManager."""
    return BillManager(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
        app_key="test_app_key",
    )


def valid_opt_in_request():
    """Creates a valid opt-in request for Bill Manager."""
    return BillManagerOptInRequest(
        shortcode=718003,
        email="youremail@gmail.com",
        officialContact="0710123456",
        sendReminders=1,
        logo="image",
        callbackurl="http://my.server.com/bar/callback",
    )


def valid_update_opt_in_request():
    """Creates a valid update opt-in request for Bill Manager."""
    return BillManagerUpdateOptInRequest(
        shortcode=718003,
        email="youremail@gmail.com",
        officialContact="0710123456",
        sendReminders=1,
        logo="image",
        callbackurl="http://my.server.com/bar/callback",
    )


def valid_single_invoice_request():
    """Creates a valid single invoice request for Bill Manager."""
    return BillManagerSingleInvoiceRequest(
        externalReference="#9932340",
        billedFullName="John Doe",
        billedPhoneNumber="0710123456",
        billedPeriod="August 2021",
        invoiceName="Jentrys",
        dueDate="2021-10-12",
        accountReference="1ASD678H",
        amount=800,
        invoiceItems=[
            {"itemName": "food", "amount": 700},
            {"itemName": "water", "amount": 100},
        ],
    )


def valid_bulk_invoice_request():
    """Creates a valid bulk invoice request for Bill Manager."""
    return BillManagerBulkInvoiceRequest(invoices=[valid_single_invoice_request()])


def valid_cancel_single_invoice_request():
    """Creates a valid cancel single invoice request for Bill Manager."""
    return BillManagerCancelSingleInvoiceRequest(externalReference="113")


def valid_cancel_bulk_invoice_request():
    """Creates a valid cancel bulk invoice request for Bill Manager."""
    return BillManagerCancelBulkInvoiceRequest(
        invoices=[
            BillManagerCancelSingleInvoiceRequest(externalReference="113"),
            BillManagerCancelSingleInvoiceRequest(externalReference="114"),
        ]
    )


def test_opt_in_success(bill_manager, mock_http_client):
    """Test successful opt-in to Bill Manager."""
    request = valid_opt_in_request()
    response_data = {
        "app_key": "AG_2376487236_126732989KJ",
        "resmsg": "Success",
        "rescode": "200",
    }
    mock_http_client.post.return_value = response_data
    response = bill_manager.opt_in(request)
    assert isinstance(response, BillManagerOptInResponse)
    assert response.app_key == response_data["app_key"]
    assert response.rescode == "200"


def test_update_opt_in_success(bill_manager, mock_http_client):
    """Test successful update of opt-in settings for Bill Manager."""
    request = valid_update_opt_in_request()
    response_data = {
        "resmsg": "Success",
        "rescode": "200",
    }
    mock_http_client.post.return_value = response_data
    response = bill_manager.update_opt_in(request)
    assert isinstance(response, BillManagerUpdateOptInResponse)
    assert response.rescode == "200"


def test_send_single_invoice_success(bill_manager, mock_http_client):
    """Test sending a single invoice via Bill Manager."""
    request = valid_single_invoice_request()
    response_data = {
        "Status_Message": "Invoice sent successfully",
        "resmsg": "Success",
        "rescode": "200",
    }
    mock_http_client.post.return_value = response_data
    response = bill_manager.send_single_invoice(request)
    assert isinstance(response, BillManagerSingleInvoiceResponse)
    assert response.is_successful() is True
    assert response.Status_Message == response_data["Status_Message"]


def test_send_bulk_invoice_success(bill_manager, mock_http_client):
    """Test sending multiple invoices via Bill Manager."""
    request = valid_bulk_invoice_request()
    response_data = {
        "Status_Message": "Invoice sent successfully",
        "resmsg": "Success",
        "rescode": "200",
    }
    mock_http_client.post.return_value = response_data
    response = bill_manager.send_bulk_invoice(request)
    assert isinstance(response, BillManagerBulkInvoiceResponse)
    assert response.Status_Message == response_data["Status_Message"]


def test_cancel_single_invoice_success(bill_manager, mock_http_client):
    """Test cancelling a single invoice via Bill Manager."""
    request = valid_cancel_single_invoice_request()
    response_data = {
        "Status_Message": "Invoice cancelled successfully.",
        "resmsg": "Success",
        "rescode": "200",
        "errors": [],
    }
    mock_http_client.post.return_value = response_data
    response = bill_manager.cancel_single_invoice(request)
    assert isinstance(response, BillManagerCancelInvoiceResponse)
    assert response.is_successful() is True
    assert response.Status_Message == response_data["Status_Message"]


def test_cancel_bulk_invoice_success(bill_manager, mock_http_client):
    """Test cancelling multiple invoices via Bill Manager."""
    request = valid_cancel_bulk_invoice_request()
    response_data = {
        "Status_Message": "Invoices cancelled successfully.",
        "resmsg": "Success",
        "rescode": "200",
        "errors": [],
    }
    mock_http_client.post.return_value = response_data
    response = bill_manager.cancel_bulk_invoice(request)
    assert isinstance(response, BillManagerCancelInvoiceResponse)
    assert response.Status_Message == response_data["Status_Message"]


def test_bill_manager_http_error(bill_manager, mock_http_client):
    """Test handling of HTTP errors when sending a single invoice."""
    request = valid_single_invoice_request()
    mock_http_client.post.side_effect = Exception("HTTP error")
    with pytest.raises(Exception) as excinfo:
        bill_manager.send_single_invoice(request)
    assert "HTTP error" in str(excinfo.value)


def test_app_key_required_for_invoice(mock_http_client, mock_token_manager):
    """Test app_key requirement for sending a single invoice."""
    manager = BillManager(
        http_client=mock_http_client, token_manager=mock_token_manager
    )
    request = valid_single_invoice_request()
    with pytest.raises(ValueError) as excinfo:
        manager.send_single_invoice(request)
    assert "app_key must be set" in str(excinfo.value)


@pytest.mark.parametrize(
    "due_date,expected",
    [
        ("2021-10-12", "2021-10-12"),
        ("2021/10/12", "2021-10-12"),
        ("2021-10-12 14:30", "2021-10-12 14:30:00"),
        ("2021-10-12 14:30:00", "2021-10-12 14:30:00.00"),
        ("2021/10/12 14:30:00", "2021-10-12 14:30:00.00"),
        ("2021-10-12 14:30:00.123", "2021-10-12 14:30:00.12"),
        ("2021-10-12 14:30:00.10", "2021-10-12 14:30:00.10"),
        ("2025-08-19T15:33:15.376886", "2025-08-19 15:33:15.37"),
    ],
)
def test_due_date_valid_formats(due_date, expected):
    """Test valid dueDate formats are accepted and normalized."""
    req = {
        "externalReference": "#9932340",
        "billedFullName": "John Doe",
        "billedPhoneNumber": "0710123456",
        "billedPeriod": "August 2021",
        "invoiceName": "Jentrys",
        "dueDate": due_date,
        "accountReference": "1ASD678H",
        "amount": 800,
        "invoiceItems": [{"itemName": "food", "amount": 700}],
    }
    result = BillManagerSingleInvoiceRequest.model_validate(req)

    # Try parsing both result.dueDate and expected to datetime objects
    def parse_due_date(date_str):
        # Try different formats based on input
        for fmt in [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y.%m.%d",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y/%m/%d %H:%M:%S.%f",
            "%Y.%m.%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y.%m.%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]:
            try:
                return datetime.strptime(date_str, fmt)
            except Exception:
                continue
        raise ValueError(f"Unrecognized date format: {date_str}")

    dt_result = parse_due_date(result.dueDate)
    dt_expected = parse_due_date(expected)
    # Compare up to the second and first two digits of microseconds
    assert dt_result.replace(
        microsecond=(dt_result.microsecond // 10000) * 10000
    ) == dt_expected.replace(microsecond=(dt_expected.microsecond // 10000) * 10000)


@pytest.mark.parametrize(
    "due_date",
    [
        "2021-13-12",  # invalid month
        "2021-10-32",  # invalid day
        "20211012",  # missing separators
        "2021-10-12 14:30:00:00",  # extra colon
        "2021-10-12 14",  # missing minutes and seconds
        "12-10-2021",  # wrong order
        "",
    ],
)
def test_due_date_invalid_formats_raise(due_date):
    """Test invalid dueDate formats raise ValueError."""
    req = {
        "externalReference": "#9932340",
        "billedFullName": "John Doe",
        "billedPhoneNumber": "0710123456",
        "billedPeriod": "August 2021",
        "invoiceName": "Jentrys",
        "dueDate": due_date,
        "accountReference": "1ASD678H",
        "amount": 800,
        "invoiceItems": [{"itemName": "food", "amount": 700}],
    }
    with pytest.raises(ValidationError) as excinfo:
        BillManagerSingleInvoiceRequest(**req)
    assert "validation error" in str(excinfo.value)


def test_due_date_missing_raises():
    """Test missing dueDate raises ValueError."""
    req = {
        "externalReference": "#9932340",
        "billedFullName": "John Doe",
        "billedPhoneNumber": "0710123456",
        "billedPeriod": "August 2021",
        "invoiceName": "Jentrys",
        # "dueDate" missing
        "accountReference": "1ASD678H",
        "amount": 800,
        "invoiceItems": [{"itemName": "food", "amount": 700}],
    }
    with pytest.raises(ValidationError) as excinfo:
        BillManagerSingleInvoiceRequest.model_validate(req)
    assert "dueDate is required" in str(excinfo.value)


def test_billed_period_invalid_raises():
    """Test invalid billedPeriod raises ValueError."""
    req = {
        "externalReference": "#9932340",
        "billedFullName": "John Doe",
        "billedPhoneNumber": "0710123456",
        "billedPeriod": "2021-08",  # invalid format
        "invoiceName": "Jentrys",
        "dueDate": "2021-10-12",
        "accountReference": "1ASD678H",
        "amount": 800,
        "invoiceItems": [{"itemName": "food", "amount": 700}],
    }
    with pytest.raises(ValueError) as excinfo:
        BillManagerSingleInvoiceRequest(**req)
    assert "billedPeriod" in str(excinfo.value)
