"""Unit tests for mpesa_sdk.mpesa_express.schemas.

This module contains unit tests for the schemas used in the mpesa_express
module of the mpesa_sdk package. The tests cover validation, normalization,
password generation, and parsing logic for STK Push requests, responses,
and callbacks.

Tested features include:
- Transaction type enums
- Phone number normalization and validation
- Password and timestamp generation
- Field length validation
- Callback metadata parsing
- Query request and response schemas
"""

import pytest
from mpesa_sdk.mpesa_express import schemas
from pydantic import ValidationError
import base64


def test_transaction_type_enum():
    """Test that TransactionType enum values are correct."""
    assert schemas.TransactionType.CUSTOMER_PAYBILL_ONLINE == "CustomerPayBillOnline"
    assert schemas.TransactionType.CUSTOMER_BUYGOODS_ONLINE == "CustomerBuyGoodsOnline"


def test_stkpush_simulate_request_password_generation_and_phone_normalization():
    """Test password generation and phone number normalization in StkPushSimulateRequest.

    Ensures that the password is generated if not provided and that the phone number
    is normalized to the correct format.
    """
    req = schemas.StkPushSimulateRequest(
        BusinessShortCode=123456,
        TransactionType="CustomerPayBillOnline",
        Amount=100,
        PartyA="0712345678",
        PartyB="123456",
        PhoneNumber="0712345678",
        CallBackURL="https://callback.url",
        AccountReference="Ref123",
        TransactionDesc="Desc",
        Passkey="abc123",
    )
    assert req.Password is not None
    assert req.PhoneNumber == "254712345678"
    assert req.Timestamp is not None
    expected_raw = f"{req.BusinessShortCode}{req.Passkey}{req.Timestamp}"
    expected_password = base64.b64encode(expected_raw.encode("utf-8")).decode("utf-8")
    assert req.Password == expected_password


def test_stkpush_simulate_request_accepts_plus254_and_0_prefix():
    """Test that StkPushSimulateRequest accepts phone numbers with +254 and 0 prefixes."""
    req = schemas.StkPushSimulateRequest(
        BusinessShortCode=123456,
        TransactionType="CustomerPayBillOnline",
        Amount=100,
        PartyA="+254712345678",
        PartyB="123456",
        PhoneNumber="+254712345678",
        CallBackURL="https://callback.url",
        AccountReference="Ref123",
        TransactionDesc="Desc",
        Passkey="abc123",
    )
    assert req.PhoneNumber == "254712345678"


def test_stkpush_simulate_request_invalid_phone_raises():
    """Test that an invalid phone number raises a ValidationError."""
    with pytest.raises(ValidationError):
        schemas.StkPushSimulateRequest(
            BusinessShortCode=123456,
            TransactionType="CustomerPayBillOnline",
            Amount=100,
            PartyA="12345678",
            PartyB="123456",
            PhoneNumber="12345678",
            CallBackURL="https://callback.url",
            AccountReference="Ref123",
            TransactionDesc="Desc",
            Passkey="abc123",
        )


def test_stkpush_simulate_request_missing_password_and_passkey_raises():
    """Test that missing both Password and Passkey raises a ValidationError."""
    with pytest.raises(ValidationError):
        schemas.StkPushSimulateRequest(
            BusinessShortCode=123456,
            TransactionType="CustomerPayBillOnline",
            Amount=100,
            PartyA="254712345678",
            PartyB="123456",
            PhoneNumber="254712345678",
            CallBackURL="https://callback.url",
            AccountReference="Ref123",
            TransactionDesc="Desc",
        )


def test_stkpush_simulate_request_account_reference_length():
    """Test that AccountReference exceeding max length raises a ValidationError."""
    with pytest.raises(ValidationError):
        schemas.StkPushSimulateRequest(
            BusinessShortCode=123456,
            TransactionType="CustomerPayBillOnline",
            Amount=100,
            PartyA="254712345678",
            PartyB="123456",
            PhoneNumber="254712345678",
            CallBackURL="https://callback.url",
            AccountReference="A" * 13,
            TransactionDesc="Desc",
            Passkey="abc123",
        )


def test_stkpush_simulate_request_transaction_desc_length():
    """Test that TransactionDesc exceeding max length raises a ValidationError."""
    with pytest.raises(ValidationError):
        schemas.StkPushSimulateRequest(
            BusinessShortCode=123456,
            TransactionType="CustomerPayBillOnline",
            Amount=100,
            PartyA="254712345678",
            PartyB="123456",
            PhoneNumber="254712345678",
            CallBackURL="https://callback.url",
            AccountReference="Ref123",
            TransactionDesc="D" * 14,
            Passkey="abc123",
        )


def test_stkpush_simulate_response_fields():
    """Test that StkPushSimulateResponse fields are set correctly."""
    resp = schemas.StkPushSimulateResponse(
        MerchantRequestID="mrid",
        CheckoutRequestID="crid",
        ResponseCode=0,
        ResponseDescription="desc",
        CustomerMessage="msg",
    )
    assert resp.MerchantRequestID == "mrid"
    assert resp.CheckoutRequestID == "crid"
    assert resp.ResponseCode == 0
    assert resp.ResponseDescription == "desc"
    assert resp.CustomerMessage == "msg"


def test_callback_metadata_item_balance_parsing():
    """Test that Balance metadata item parses BasicAmount from string."""
    # Test with string representation of BasicAmount
    item = schemas.StkPushSimulateCallbackMetadataItem(
        Name="Balance",
        Value="{Amount={BasicAmount=123.45, MinLimit=0.00, MaxLimit=0.00}}",
    )
    assert item.Value == 123.45

    # Test with float value
    item = schemas.StkPushSimulateCallbackMetadataItem(
        Name="Balance",
        Value=123.45,  # Should be a float, not a string
    )
    assert item.Value == 123.45

    # Test with an anomally response
    item = schemas.StkPushSimulateCallbackMetadataItem(
        Name="Balance",
        Value="another string that is not a valid balance",
    )
    assert item.Value == "another string that is not a valid balance"


def test_callback_metadata_item_balance_parsing_invalid_float(monkeypatch):
    """Test that if BasicAmount is present but not a valid float, ValueError is handled gracefully."""

    # Patch re.search to return a match with a non-numeric string
    class FakeMatch:
        def group(self, idx):
            return "not_a_float"

    def fake_search(pattern, string):
        return FakeMatch()

    monkeypatch.setattr(schemas.re, "search", fake_search)
    # Should not raise, Value should remain the original string
    item = schemas.StkPushSimulateCallbackMetadataItem(
        Name="Balance",
        Value="{Amount={BasicAmount=not_a_float}}",
    )
    assert item.Value == "{Amount={BasicAmount=not_a_float}}"


def test_callback_metadata_item_non_balance_untouched():
    """Test that non-Balance metadata items are not modified."""
    item = schemas.StkPushSimulateCallbackMetadataItem(Name="Amount", Value=100)
    assert item.Value == 100


def test_stkpush_simulate_callback_properties():
    """Test properties of StkPushSimulateCallback for correct parsing and success detection."""
    callback = schemas.StkPushSimulateCallback.model_validate(
        {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "mrid",
                    "CheckoutRequestID": "crid",
                    "ResultCode": 0,
                    "ResultDesc": "desc",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 100.0},
                            {"Name": "MpesaReceiptNumber", "Value": "ABC123"},
                            {"Name": "Balance", "Value": "{Amount={BasicAmount=50.5}}"},
                            {"Name": "TransactionDate", "Value": 20240607123456},
                            {"Name": "PhoneNumber", "Value": 254712345678},
                        ]
                    },
                }
            }
        }
    )
    assert callback.amount == 100.0
    assert callback.mpesa_receipt_number == "ABC123"
    assert callback.balance == 50.5
    assert callback.transaction_date == "20240607123456"
    assert callback.phone_number == "254712345678"
    assert callback.is_successful is True

    # test that non-existent attributes return None
    assert callback.get_metadata_value("NonExistent") is None


def test_stkpush_simulate_callback_missing_metadata_returns_none():
    """Test that missing CallbackMetadata returns None for metadata properties."""
    callback = schemas.StkPushSimulateCallback.model_validate(
        {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "mrid",
                    "CheckoutRequestID": "crid",
                    "ResultCode": 1,
                    "ResultDesc": "desc",
                    "CallbackMetadata": None,
                }
            }
        }
    )
    assert callback.amount is None
    assert callback.is_successful is False


def test_stkpush_query_request_password_generation():
    """Test password and timestamp generation in StkPushQueryRequest."""
    req = schemas.StkPushQueryRequest(
        BusinessShortCode=123456, CheckoutRequestID="crid", Passkey="abc123"
    )
    assert req.Password is not None
    assert req.Timestamp is not None
    expected_raw = f"{req.BusinessShortCode}{req.Passkey}{req.Timestamp}"
    expected_password = base64.b64encode(expected_raw.encode("utf-8")).decode("utf-8")
    assert req.Password == expected_password


def test_stkpush_query_request_missing_password_and_passkey_raises():
    """Test that missing both Password and Passkey in StkPushQueryRequest raises ValidationError."""
    with pytest.raises(ValidationError):
        schemas.StkPushQueryRequest(BusinessShortCode=123456, CheckoutRequestID="crid")


def test_stkpush_query_request_password_provided_without_timestamp_raises():
    """Test that providing Password without Timestamp in StkPushQueryRequest raises a ValidationError."""
    # __init__ sets Timestamp if missing, so we must call the validator directly
    with pytest.raises(ValidationError) as excinfo:
        schemas.StkPushQueryRequest(
            BusinessShortCode=123456,
            Password="bXlwYXNzd29yZA==",
            CheckoutRequestID="crid",
            # No Timestamp, no Passkey
        )
    assert "If 'Password' is provided, 'Timestamp' must also be provided" in str(
        excinfo.value
    )


def test_stkpush_query_response_fields():
    """Test that StkPushQueryResponse fields are set correctly."""
    resp = schemas.StkPushQueryResponse(
        MerchantRequestID="mrid",
        CheckoutRequestID="crid",
        ResponseCode=0,
        ResponseDescription="desc",
        ResultCode=0,
        ResultDesc="result",
    )
    assert resp.MerchantRequestID == "mrid"
    assert resp.CheckoutRequestID == "crid"
    assert resp.ResponseCode == 0
    assert resp.ResponseDescription == "desc"
    assert resp.ResultCode == 0
    assert resp.ResultDesc == "result"


def test_stkpush_simulate_request_password_provided_without_timestamp_raises():
    """Test that providing Password without Timestamp raises a ValidationError."""
    # Even though __init__ sets Timestamp if missing, test the validator logic directly
    with pytest.raises(ValidationError) as excinfo:
        schemas.StkPushSimulateRequest(
            BusinessShortCode=123456,
            Password="bXlwYXNzd29yZA==",
            TransactionType="CustomerPayBillOnline",
            Amount=100,
            PartyA="254712345678",
            PartyB="123456",
            PhoneNumber="254712345678",
            CallBackURL="https://callback.url",
            AccountReference="Ref123",
            TransactionDesc="Desc",
        )
    # The error message should mention both Password and Timestamp
    assert "If 'Password' is provided, 'Timestamp' must also be provided" in str(
        excinfo.value
    )


def test_stkpush_simulate_request_paybill_requires_account_reference():
    """Test that AccountReference is required for CustomerPayBillOnline TransactionType."""
    with pytest.raises(ValidationError) as excinfo:
        schemas.StkPushSimulateRequest(
            BusinessShortCode=123456,
            TransactionType="CustomerPayBillOnline",
            Amount=100,
            PartyA="254712345678",
            PartyB="123456",
            PhoneNumber="254712345678",
            CallBackURL="https://callback.url",
            TransactionDesc="Desc",
            Passkey="abc123",
        )
    assert "AccountReference must be provided when using PayBill" in str(excinfo.value)
