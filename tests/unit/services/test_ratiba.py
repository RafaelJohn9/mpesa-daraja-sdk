"""Unit tests for the RatibaService facade in mpesa_sdk.services.ratiba module."""

import pytest
from unittest.mock import MagicMock
from mpesa_sdk.services.ratiba import RatibaService
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.mpesa_ratiba import (
    StandingOrderRequest,
    StandingOrderResponse,
    TransactionTypeEnum,
    ReceiverPartyIdentifierTypeEnum,
    FrequencyEnum,
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
def ratiba_service(mock_http_client, mock_token_manager):
    """Creates a RatibaService instance for testing."""
    return RatibaService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
    )


def test_create_standing_order_success(ratiba_service, mock_http_client):
    """Test successful Standing Order creation."""
    response = {
        "ResponseHeader": {
            "responseRefID": "4dd9b5d9-d738-42ba-9326-2cc99e966000",
            "responseCode": "200",
            "responseDescription": "Request accepted for processing",
            "ResultDesc": "The service request is processed successfully.",
        },
        "ResponseBody": {
            "responseDescription": "Request accepted for processing",
            "responseCode": "200",
        },
    }
    mock_http_client.post.return_value = response

    resp = ratiba_service.create_standing_order(
        standing_order_name="MyOrder",
        start_date="20240601",
        end_date="20241201",
        business_short_code="123456",
        transaction_type=TransactionTypeEnum.STANDING_ORDER_CUSTOMER_PAY_BILL,
        receiver_party_identifier_type=ReceiverPartyIdentifierTypeEnum.BUSINESS_SHORT_CODE,
        amount="1000",
        party_a="254712345678",
        callback_url="https://example.com/callback",
        account_reference="Ref123",
        transaction_desc="Monthly Pay",
        frequency=FrequencyEnum.MONTHLY,
    )

    assert isinstance(resp, StandingOrderResponse)
    assert resp.is_successful() is True


def test_create_standing_order_filters_kwargs(ratiba_service, mock_http_client):
    """Test that extra kwargs are filtered out in create_standing_order."""
    response = {
        "ResponseHeader": {
            "responseRefID": "4dd9b5d9-d738-42ba-9326-2cc99e966000",
            "responseCode": "200",
            "responseDescription": "Request accepted for processing",
            "ResultDesc": "The service request is processed successfully.",
        },
        "ResponseBody": {
            "responseDescription": "Request accepted for processing",
            "responseCode": "200",
        },
    }
    mock_http_client.post.return_value = response

    resp = ratiba_service.create_standing_order(
        standing_order_name="Order2",
        start_date="20240601",
        end_date="20241201",
        business_short_code="654321",
        transaction_type=TransactionTypeEnum.STANDING_ORDER_CUSTOMER_PAY_BILL,
        receiver_party_identifier_type=ReceiverPartyIdentifierTypeEnum.BUSINESS_SHORT_CODE,
        amount="500",
        party_a="254798765432",
        callback_url="https://example.com/callback2",
        account_reference="Ref456",
        transaction_desc="Weekly pay",
        frequency=FrequencyEnum.WEEKLY,
        ExtraField="should_be_filtered",
    )

    assert isinstance(resp, StandingOrderResponse)
    assert resp.is_successful() is True
    assert not hasattr(resp, "ExtraField")


def test_ratiba_service_initializes_ratiba_correctly(
    mock_http_client, mock_token_manager
):
    """Test RatibaService initializes MpesaRatiba with correct arguments."""
    service = RatibaService(
        http_client=mock_http_client,
        token_manager=mock_token_manager,
    )
    assert service.http_client is mock_http_client
    assert service.token_manager is mock_token_manager
    assert service.ratiba.http_client is mock_http_client
    assert service.ratiba.token_manager is mock_token_manager
