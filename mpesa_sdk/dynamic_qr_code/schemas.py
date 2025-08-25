"""mpesa_sdk.dynamic_qr_code.schemas.

This module defines the schemas for generating a dynamic M-Pesa QR code.
It includes request and response models using Pydantic for validation and serialization.
"""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from pydantic import model_validator
from mpesa_sdk.utils.phone import normalize_phone_number


class DynamicQRTransactionType(str, Enum):
    """Enum representing the supported transaction types for Dynamic QR."""

    BUY_GOODS = "BG"  # Pay Merchant (Buy Goods)
    WITHDRAW_CASH = "WA"  # Withdraw Cash at Agent Till
    PAYBILL = "PB"  # Paybill or Business number
    SEND_MONEY = "SM"  # Send Money (Mobile number)
    SEND_TO_BUSINESS = "SB"  # Sent to Business (Business number CPI in MSISDN format)


class DynamicQRGenerateRequest(BaseModel):
    """Represents the request payload for generating a Dynamic QR code.

    https://developer.safaricom.co.ke/APIs/DynamicQRCode

    Attributes:
        MerchantName (str): Name of the Company/M-Pesa Merchant Name.
        RefNo (str): Transaction Reference. For Paybill, Withdraw Cash, and similar transactions, this is where you enter your account number.
        Amount (float): The total amount for the sale/transaction.
        TrxCode (DynamicQRTransactionType): Transaction Type.
        CPI (str): Credit Party Identifier (Mobile Number, Business Number, Agent Till, Paybill, etc.).
        Size (str): Size of the QR code image in pixels (always a square image).
    """

    MerchantName: str = Field(
        ...,
        description="Name of the Company/M-Pesa Merchant Name.",
        examples=["TEST SUPERMARKET"],
    )
    RefNo: str = Field(
        ...,
        description="Transaction Reference. For Paybill, Withdraw Cash, and similar transactions, this is where you enter your account number.",
        examples=["Invoice Test", "xewr34fer4t", "ACC12345"],
    )
    Amount: int = Field(
        ...,
        description="The total amount for the sale/transaction.",
        examples=[1, 2000],
        gt=0,
    )
    TrxCode: str = Field(
        ...,
        description="Transaction Type. Supported: BG, WA, PB, SM, SB.",
        examples=["BG"],
    )

    CPI: str = Field(
        ...,
        description="Credit Party Identifier. Can be a Mobile Number, Business Number, Agent Till, Paybill or Business number, or Merchant Buy Goods.",
        examples=["373132", "174379"],
    )
    Size: str = Field(
        ...,
        description="Size of the QR code image in pixels. QR code image will always be a square image.",
        examples=["300"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "MerchantName": "TEST SUPERMARKET",
                "RefNo": "Invoice Test",
                "Amount": 1,
                "TrxCode": "BG",
                "CPI": "373132",
                "Size": "300",
            }
        }
    )

    @model_validator(mode="before")
    def validate(cls, values):
        """Validates the TrxCode field before model validation."""
        # Validate the TrxCode field
        trx_code = values.get("TrxCode")
        if trx_code is not None:
            cls._validate_trx_code(trx_code)

        # Normalize CPI for SEND_MONEY transaction type
        cls._normalize_cpi_for_send_money(values)

        return values

    @classmethod
    def _validate_trx_code(cls, value):
        """Validates the transaction code against the DynamicQRTransactionType enum."""
        try:
            DynamicQRTransactionType(value)
        except ValueError:
            raise ValueError(
                f"TrxCode must be one of: {[e.value for e in DynamicQRTransactionType]}"
            )
        return value

    @classmethod
    def _normalize_cpi_for_send_money(cls, values):
        """If TrxCode is SEND_MONEY, normalize the CPI (mobile number).

        - If it starts with '0', replace with '254'
        - If it starts with '+254', replace with '254'
        - If it can't be normalized, raise ValueError
        """
        trx_code = values.get("TrxCode")
        cpi = values.get("CPI")
        if trx_code == DynamicQRTransactionType.SEND_MONEY.value and isinstance(
            cpi, str
        ):
            normalized = normalize_phone_number(cpi)
            if normalized is None:
                raise ValueError(
                    "CPI for SEND_MONEY must be a valid Kenyan phone number starting with '0', '+254', or '254'."
                )
            values["CPI"] = normalized
        return values


class DynamicQRGenerateResponse(BaseModel):
    """Represents the response returned after generating a Dynamic QR code.

    https://developer.safaricom.co.ke/APIs/DynamicQRCode

    Attributes:
        ResponseCode (str): Used to return the Transaction Type (alpha-numeric string).
        RequestID (str): Unique identifier for the request.
        ResponseDescription (str): Description of the transaction status.
        QRCode (str): QR Code Image/Data/String (base64 or similar).
    """

    ResponseCode: str | int = Field(
        ...,
        description="Used to show if the transaction was successful or not. 00 indicates success.",
        examples=["00"],
    )
    ResponseDescription: str = Field(
        ...,
        description="This is a response describing the status of the transaction.",
        examples=["QR Code Successfully Generated."],
    )
    QRCode: str = Field(
        ...,
        description="QR Code Image/Data/String.",
        examples=["iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAIAAAD2HxkiAAAHtElEQVR42..."],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ResponseCode": "00",
                "RequestID": "16738-27456357-1",
                "ResponseDescription": "QR Code Successfully Generated.",
                "QRCode": "iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAIAAAD2HxkiAAAHtElEQVR42...",
            }
        }
    )

    def is_successful(self) -> bool:
        """Return True if ResponseCode indicates success (e.g., '0', '00000000')."""
        code = str(self.ResponseCode)
        # Remove zeros and check if the result is empty (i.e., all zeros)
        return code.strip("0") == "" and code != ""
