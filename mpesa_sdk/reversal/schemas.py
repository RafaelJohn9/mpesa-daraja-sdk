"""This module defines schemas for M-Pesa Reversal API requests and responses.

It includes models for reversal requests, responses, and result notifications.
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List


class ReversalRequest(BaseModel):
    """Request schema for Transaction Reversal."""

    Initiator: str = Field(..., description="Username used to initiate the request.")
    SecurityCredential: str = Field(..., description="Encrypted security credential.")
    TransactionID: str = Field(..., description="Mpesa Transaction ID to reverse.")
    Amount: int = Field(..., description="Amount to reverse (in KES).")
    ReceiverParty: int = Field(..., description="Organization shortcode (6-9 digits).")
    ResultURL: str = Field(..., description="URL for result notifications.")
    QueueTimeOutURL: str = Field(..., description="URL for timeout notifications.")
    Remarks: str = Field(
        ..., description="Comments for the transaction (max 100 chars)."
    )
    Occasion: Optional[str] = Field(
        None, description="Optional parameter (max 100 chars)."
    )

    CommandID: str = "TransactionReversal"
    RecieverIdentifierType: str = "11"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Initiator": "TestInit610",
                "SecurityCredential": "encrypted_credential",
                "CommandID": "TransactionReversal",
                "TransactionID": "LKXXXX1234",
                "Amount": 100,
                "ReceiverParty": 600610,
                "RecieverIdentifierType": "11",
                "ResultURL": "https://ip:port/result",
                "QueueTimeOutURL": "https://ip:port/timeout",
                "Remarks": "Test",
                "Occasion": "work",
            }
        }
    )

    @model_validator(mode="before")
    @classmethod
    def validate(cls, values):
        """Validates model."""
        cls._validate_remarks(values)
        cls._validate_occasion(values)
        return values

    @classmethod
    def _validate_remarks(cls, values):
        remarks = values.get("Remarks")
        if remarks is not None and len(remarks) > 100:
            raise ValueError("Remarks must not exceed 100 characters.")
        return values

    @classmethod
    def _validate_occasion(cls, values):
        occasion = values.get("Occasion")
        if occasion is not None and len(occasion) > 100:
            raise ValueError("Occasion must not exceed 100 characters.")
        return values


class ReversalResponse(BaseModel):
    """Response schema for Transaction Reversal request."""

    OriginatorConversationID: Optional[str] = Field(
        ..., description="Unique ID for the request message."
    )
    ConversationID: Optional[str] = Field(
        ..., description="Unique ID for the transaction."
    )
    ResponseCode: str | int = Field(..., description="Status code, 0 means success.")
    ResponseDescription: str = Field(..., description="Status message.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "OriginatorConversationID": "71840-27539181-07",
                "ConversationID": "AG_20210709_12346c8e6f8858d7b70a",
                "ResponseCode": "0",
                "ResponseDescription": "Accept the service request successfully.",
            }
        }
    )

    def is_successful(self) -> bool:
        """Check if the response indicates success."""
        code = str(self.ResponseCode)
        return code.strip("0") == "" and code != ""


class ReversalResultParameter(BaseModel):
    """Parameter item in Reversal result notification."""

    Key: str = Field(..., description="Parameter name.")
    Value: str = Field(..., description="Parameter value.")


class ReversalReferenceItem(BaseModel):
    """Reference item in Reversal result notification."""

    Key: str = Field(..., description="Reference parameter name.")
    Value: str = Field(..., description="Reference parameter value.")


class ReversalReferenceData(BaseModel):
    """Reference data in Reversal result notification."""

    ReferenceItem: ReversalReferenceItem = Field(..., description="Reference item.")


class ReversalResultParameters(BaseModel):
    """Result parameters container."""

    ResultParameter: List[ReversalResultParameter] = Field(
        ..., description="List of result parameters."
    )


class ReversalResultMetadata(BaseModel):
    """Metadata for Reversal result notification."""

    ResultType: int = Field(..., description="Type of result (0=Success, 1=Waiting).")
    ResultCode: str = Field(..., description="Result code (0=Success).")
    ResultDesc: str = Field(..., description="Result description.")
    OriginatorConversationID: str = Field(
        ..., description="Originator conversation ID."
    )
    ConversationID: str = Field(..., description="Conversation ID.")
    TransactionID: Optional[str] = Field(
        None, description="M-Pesa transaction ID (if available)."
    )
    ResultParameters: Optional[ReversalResultParameters] = Field(
        None, description="Result parameters container."
    )
    ReferenceData: Optional[ReversalReferenceData] = Field(
        None, description="Reference data."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ResultType": 0,
                "ResultCode": "21",
                "ResultDesc": "The service request is processed successfully",
                "OriginatorConversationID": "8521-4298025-1",
                "ConversationID": "AG_20181005_00004d7ee675c0c7ee0b",
                "TransactionID": "MJ561H6X5O",
                "ResultParameters": {
                    "ResultParameter": [
                        {
                            "Key": "DebitAccountBalance",
                            "Value": "Utility Account|KES|51661.00|51661.00|0.00|0.00",
                        },
                        {"Key": "Amount", "Value": "100"},
                        {"Key": "TransCompletedTime", "Value": "20181005153225"},
                        {"Key": "OriginalTransactionID", "Value": "MJ551H6X5D"},
                        {"Key": "Charge", "Value": "0"},
                        {
                            "Key": "CreditPartyPublicName",
                            "Value": "254708374149 - John Doe",
                        },
                        {
                            "Key": "DebitPartyPublicName",
                            "Value": "601315 - Safaricom1338",
                        },
                    ]
                },
                "ReferenceData": {
                    "ReferenceItem": {
                        "Key": "QueueTimeoutURL",
                        "Value": "https://internalsandbox.safaricom.co.ke/mpesa/reversalresults/v1/submit",
                    }
                },
            }
        }
    )


class ReversalResultCallback(BaseModel):
    """Schema for Reversal result notification sent to ResultURL."""

    Result: ReversalResultMetadata = Field(..., description="Result metadata.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Result": {
                    "ResultType": 0,
                    "ResultCode": "21",
                    "ResultDesc": "The service request is processed successfully",
                    "OriginatorConversationID": "8521-4298025-1",
                    "ConversationID": "AG_20181005_00004d7ee675c0c7ee0b",
                    "TransactionID": "MJ561H6X5O",
                    "ResultParameters": {
                        "ResultParameter": [
                            {
                                "Key": "DebitAccountBalance",
                                "Value": "Utility Account|KES|51661.00|51661.00|0.00|0.00",
                            },
                            {"Key": "Amount", "Value": "100"},
                            {"Key": "TransCompletedTime", "Value": "20181005153225"},
                            {"Key": "OriginalTransactionID", "Value": "MJ551H6X5D"},
                            {"Key": "Charge", "Value": "0"},
                            {
                                "Key": "CreditPartyPublicName",
                                "Value": "254708374149 - John Doe",
                            },
                            {
                                "Key": "DebitPartyPublicName",
                                "Value": "601315 - Safaricom1338",
                            },
                        ]
                    },
                    "ReferenceData": {
                        "ReferenceItem": {
                            "Key": "QueueTimeoutURL",
                            "Value": "https://internalsandbox.safaricom.co.ke/mpesa/reversalresults/v1/submit",
                        }
                    },
                }
            }
        }
    )


class ReversalResultCallbackResponse(BaseModel):
    """Schema for response to Reversal result callback."""

    ResultCode: int = Field(
        default=0, description="Result code (0=Success, other=Failure)."
    )
    ResultDesc: str = Field(
        default="Result received and processed successfully.",
        description="Result description.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ResultCode": 0,
                "ResultDesc": "Result received and processed successfully.",
            }
        }
    )


class ReversalTimeoutCallback(BaseModel):
    """Schema for Reversal timeout notification sent to QueueTimeOutURL."""

    Result: ReversalResultMetadata = Field(..., description="Result metadata.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Result": {
                    "ResultType": 1,
                    "ResultCode": "1",
                    "ResultDesc": "The service request timed out.",
                    "OriginatorConversationID": "8521-4298025-1",
                    "ConversationID": "AG_20181005_00004d7ee675c0c7ee0b",
                }
            }
        }
    )


class ReversalTimeoutCallbackResponse(BaseModel):
    """Schema for response to Reversal timeout callback."""

    ResultCode: int = Field(
        default=0,
        description="Result code (0=Success, other=Failure).",
    )
    ResultDesc: str = Field(
        default="Timeout notification received and processed successfully.",
        description="Result description.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ResultCode": 0,
                "ResultDesc": "Timeout notification received and processed successfully.",
            }
        }
    )
