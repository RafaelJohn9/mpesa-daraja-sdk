"""Schemas for M-PESA Bill Manager APIs."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr, HttpUrl, model_validator
from typing import Optional, List, Any
import re


# Onboarding (Opt-in) API
class BillManagerOptInRequest(BaseModel):
    """Request schema for onboarding (opt-in) to the M-PESA Bill Manager."""

    shortcode: int = Field(
        ..., description="Organization's shortcode (Paybill/Buygoods)."
    )
    email: EmailStr = Field(..., description="Official contact email address.")
    officialContact: str = Field(..., description="Official contact phone number.")
    sendReminders: int = Field(
        ..., description="Enable(1)/Disable(0) SMS payment reminders."
    )
    logo: Optional[str] = Field(
        None, description="Image (JPEG/JPG) to embed in invoices/receipts."
    )
    callbackurl: HttpUrl = Field(
        ..., description="Callback URL for payment notifications."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "shortcode": 718003,
                "email": "youremail@gmail.com",
                "officialContact": "0710123456",
                "sendReminders": 1,
                "logo": "image",
                "callbackurl": "http://my.server.com/bar/callback",
            }
        }
    )


class BillManagerOptInResponse(BaseModel):
    """Response schema for onboarding (opt-in) to the M-PESA Bill Manager."""

    app_key: str = Field(..., description="App key received upon onboarding.")
    resmsg: str = Field(..., description="Status message.")
    rescode: str = Field(..., description="Status code (200=success).")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "app_key": "AG_2376487236_126732989KJ",
                "resmsg": "Success",
                "rescode": "200",
            }
        }
    )

    def is_successful(self) -> bool:
        """Checks if the response indicates success."""
        return self.rescode == "200"


# Update Opt-in Details API
class BillManagerUpdateOptInRequest(BaseModel):
    """Request schema for updating opt-in details in the M-PESA Bill Manager."""

    shortcode: int = Field(..., description="Organization's shortcode.")
    email: EmailStr = Field(..., description="Official contact email address.")
    officialContact: str = Field(..., description="Official contact phone number.")
    sendReminders: int = Field(
        ..., description="Enable(1)/Disable(0) SMS payment reminders."
    )
    logo: Optional[str] = Field(
        None, description="Image (JPEG/JPG) to embed in invoices/receipts."
    )
    callbackurl: Optional[str] = Field(
        None, description="Callback URL for payment notifications."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "shortcode": 718003,
                "email": "youremail@gmail.com",
                "officialContact": "0710123456",
                "sendReminders": 1,
                "logo": "image",
                "callbackurl": "/api.example.com/payments?callbackURL=http://my.server.com/bar",
            }
        }
    )


class BillManagerUpdateOptInResponse(BaseModel):
    """Response schema for updating opt-in details in the M-PESA Bill Manager."""

    resmsg: str = Field(..., description="Status message.")
    rescode: str = Field(..., description="Status code (200=success).")

    model_config = ConfigDict(
        json_schema_extra={"example": {"resmsg": "Success", "rescode": "200"}}
    )

    def is_successful(self) -> bool:
        """Checks if the response indicates success."""
        return self.rescode == "200"


# Invoice Item
class InvoiceItem(BaseModel):
    """Schema for an item in the invoice."""

    itemName: str = Field(..., description="Name of the invoice item.")
    amount: int = Field(..., description="Amount for the item.")

    model_config = ConfigDict(
        json_schema_extra={"example": {"itemName": "food", "amount": 700}}
    )


# Single Invoicing API
class BillManagerSingleInvoiceRequest(BaseModel):
    """Request schema for sending a single invoice via M-PESA Bill Manager."""

    externalReference: str = Field(
        ..., description="Unique invoice reference on your system."
    )
    billedFullName: str = Field(..., description="Recipient's full name.")
    billedPhoneNumber: str = Field(
        ..., description="Recipient's Safaricom phone number."
    )
    billedPeriod: str = Field(
        ..., description="Month and year billed (e.g. August 2021)."
    )
    invoiceName: str = Field(..., description="Descriptive invoice name.")
    dueDate: str = Field(
        ..., description="Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)."
    )
    accountReference: str = Field(..., description="Account number being invoiced.")
    amount: int = Field(..., description="Total invoice amount in KES.")
    invoiceItems: Optional[List[InvoiceItem]] = Field(
        None, description="Additional billable items."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "externalReference": "#9932340",
                "billedFullName": "John Doe",
                "billedPhoneNumber": "0710123456",
                "billedPeriod": "August 2021",
                "invoiceName": "Jentrys",
                "dueDate": "2021-10-12",
                "accountReference": "1ASD678H",
                "amount": 800,
                "invoiceItems": [
                    {"itemName": "food", "amount": 700},
                    {"itemName": "water", "amount": 100},
                ],
            }
        }
    )

    @model_validator(mode="before")
    @classmethod
    def validate(cls, values):
        """Validates the input data and raises ValueError if billedPeriod is invalid.

        Returns an instance of BillManagerSingleInvoiceRequest if valid.
        """
        cls._validate_billed_period(values)
        cls._validate_and_format_due_date(values)

        return values

    @classmethod
    def _validate_and_format_due_date(cls, values):
        """Validates and reformats the due date.

        Returns date in 'YYYY-MM-DD' if only date is provided,
        or 'YYYY-MM-DD HH:MM:SS' if time is included.
        Raises ValueError if format is invalid or date/time values are out of range.
        """
        due_date = values.get("dueDate")
        if not due_date:
            raise ValueError("dueDate is required.")

        # Normalize separators to '-'
        normalized_due_date = re.sub(r"[\/]", "-", due_date)
        # Replace 'T' with space
        normalized_due_date = normalized_due_date.replace("T", " ")

        # Match date only: YYYY-MM-DD
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        # Match datetime: YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM:SS.sss
        datetime_pattern = r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?(\.\d+)?$"

        try:
            if re.match(date_pattern, normalized_due_date):
                # Try to parse as date
                parsed_date = datetime.strptime(normalized_due_date, "%Y-%m-%d")
                values["dueDate"] = parsed_date.strftime("%Y-%m-%d")
            elif re.match(datetime_pattern, normalized_due_date):
                # Handle different time formats
                date_part, time_part = normalized_due_date.split(" ", 1)
                time_part = time_part.replace("T", " ")

                # Split time components
                if "." in time_part:
                    time_main, ms_part = time_part.split(".", 1)
                    ms_part = ms_part[:2].ljust(
                        2, "0"
                    )  # Keep only 2 digits, pad with 0
                else:
                    time_main = time_part
                    ms_part = "00"

                # Handle HH:MM vs HH:MM:SS
                time_components = time_main.split(":")
                if len(time_components) == 2:
                    # HH:MM format - append :00 for seconds
                    time_main = f"{time_main}:00"
                elif len(time_components) == 3:
                    # HH:MM:SS format - keep as is
                    pass

                # Parse the full datetime
                if "." in normalized_due_date:
                    parsed_datetime = datetime.strptime(
                        f"{date_part} {time_main}.{ms_part}", "%Y-%m-%d %H:%M:%S.%f"
                    )
                    # Format with milliseconds
                    values["dueDate"] = parsed_datetime.strftime(
                        f"%Y-%m-%d %H:%M:%S.{ms_part}"
                    )
                else:
                    parsed_datetime = datetime.strptime(
                        f"{date_part} {time_main}", "%Y-%m-%d %H:%M:%S"
                    )
                    values["dueDate"] = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S.00")
            else:
                raise ValueError(
                    "dueDate must be in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM(:SS)(.sss)' format."
                )
        except ValueError as e:
            # Re-raise any parsing errors as ValueError
            raise ValueError(str(e)) from e

    @classmethod
    def _validate_billed_period(cls, values):
        """Validates that billed_period is in the format 'Month YYYY' (e.g., 'August 2021').

        Returns True if valid, False otherwise.
        """
        billed_period = values.get("billedPeriod")
        pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$"
        if not re.match(pattern, billed_period):
            raise ValueError(
                "billedPeriod must be in the format 'Month YYYY' (e.g., 'August 2021') and use a valid month name (January, February - December)."
            )


class BillManagerSingleInvoiceResponse(BaseModel):
    """Response schema for sending a single invoice via M-PESA Bill Manager."""

    Status_Message: str = Field(..., description="Descriptive status message.")
    resmsg: str = Field(..., description="Status message.")
    rescode: str = Field(..., description="Status code (200=success).")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Status_Message": "Invoice sent successfully",
                "resmsg": "Success",
                "rescode": "200",
            }
        }
    )

    def is_successful(self) -> bool:
        """Checks if the response indicates success."""
        return self.rescode == "200"


# Bulk Invoicing API
class BillManagerBulkInvoiceRequest(BaseModel):
    """Request schema for sending multiple invoices via M-PESA Bill Manager."""

    invoices: List[BillManagerSingleInvoiceRequest] = Field(
        ..., description="List of invoices to send (max 1000)."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "invoices": [
                    {
                        "externalReference": "1107",
                        "billedFullName": "John Doe",
                        "billedPhoneNumber": "0722000000",
                        "billedPeriod": "August 2021",
                        "invoiceName": "Jentrys",
                        "dueDate": "2021-09-15 00:00:00.00",
                        "accountReference": "A1",
                        "amount": 2000,
                        "invoiceItems": [
                            {"itemName": "food", "amount": 1000},
                            {"itemName": "water", "amount": 1000},
                        ],
                    }
                ]
            }
        }
    )


class BillManagerBulkInvoiceResponse(BaseModel):
    """Response schema for sending multiple invoices via M-PESA Bill Manager."""

    Status_Message: str = Field(..., description="Descriptive status message.")
    resmsg: str = Field(..., description="Status message.")
    rescode: str = Field(..., description="Status code (200=success).")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Status_Message": "Invoice sent successfully",
                "resmsg": "Success",
                "rescode": "200",
            }
        }
    )

    def is_successful(self) -> bool:
        """Checks if the response indicates success."""
        return self.rescode == "200"


# Cancel Single Invoice API
class BillManagerCancelSingleInvoiceRequest(BaseModel):
    """Request schema for cancelling a single invoice via M-PESA Bill Manager."""

    externalReference: str = Field(
        ..., description="External reference of invoice to cancel."
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"externalReference": "113"}}
    )


# Cancel Bulk Invoice API
class BillManagerCancelBulkInvoiceRequest(BaseModel):
    """Request schema for cancelling multiple invoices via M-PESA Bill Manager."""

    invoices: List[BillManagerCancelSingleInvoiceRequest] = Field(
        ..., description="List of invoices to cancel."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "invoices": [{"externalReference": "113"}, {"externalReference": "114"}]
            }
        }
    )


class BillManagerCancelInvoiceResponse(BaseModel):
    """Response schema for cancelling an invoice via M-PESA Bill Manager."""

    Status_Message: str = Field(..., description="Descriptive status message.")
    resmsg: str = Field(..., description="Status message.")
    rescode: str = Field(..., description="Status code (200=success, 409=conflict).")
    errors: Optional[List[Any]] = Field(default=None, description="List of errors.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Status_Message": "Invoice cancelled successfully.",
                "resmsg": "Success",
                "rescode": "200",
                "errors": [],
            }
        }
    )

    def is_successful(self) -> bool:
        """Checks if the response indicates success."""
        return self.rescode == "200"


# Payment Notification (Callback) API
class BillManagerPaymentNotificationRequest(BaseModel):
    """Request schema for M-PESA Bill Manager payment notification callback (from Mpesa)."""

    transactionId: str = Field(..., description="M-PESA generated reference.")
    paidAmount: int = Field(..., description="Amount paid in KES.")
    msisdn: str = Field(..., description="Customer's phone number debited.")
    dateCreated: str = Field(..., description="Date payment was recorded (YYYY-MM-DD).")
    accountReference: str = Field(..., description="Account number being invoiced.")
    shortCode: int = Field(..., description="Organization's shortcode.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transactionId": "RJB53MYR1N",
                "paidAmount": 5000,
                "msisdn": "254722000000",
                "dateCreated": "2021-10-01",
                "accountReference": "BC001",
                "shortCode": 456545,
            }
        }
    )


class BillManagerPaymentNotificationResponse(BaseModel):
    """Response schema for M-PESA Bill Manager payment notification callback."""

    resmsg: str = Field(..., description="Status message.")
    rescode: str = Field(..., description="Status code (200=success).")

    model_config = ConfigDict(
        json_schema_extra={"example": {"resmsg": "Success", "rescode": "200"}}
    )


# Payment Acknowledgment API
class BillManagerPaymentAcknowledgmentRequest(BaseModel):
    """Request schema for acknowledging a payment via M-PESA Bill Manager."""

    paymentDate: str = Field(..., description="Date payment was settled (YYYY-MM-DD).")
    paidAmount: int = Field(..., description="Amount paid in KES.")
    accountReference: str = Field(..., description="Account number being invoiced.")
    transactionId: str = Field(..., description="M-PESA generated reference.")
    phoneNumber: str = Field(..., description="Customer's phone number.")
    fullName: str = Field(..., description="Customer's full name.")
    invoiceName: str = Field(..., description="Invoice name.")
    externalReference: str = Field(..., description="External invoice reference.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "paymentDate": "2021-10-01",
                "paidAmount": 800,
                "accountReference": "Balboa95",
                "transactionId": "PJB53MYR1N",
                "phoneNumber": "0710123456",
                "fullName": "John Doe",
                "invoiceName": "School Fees",
                "externalReference": "955",
            }
        }
    )


class BillManagerPaymentAcknowledgmentResponse(BaseModel):
    """Response schema for acknowledging a payment via M-PESA Bill Manager."""

    resmsg: str = Field(..., description="Status message.")
    rescode: str = Field(..., description="Status code (200=success).")

    model_config = ConfigDict(
        json_schema_extra={"example": {"resmsg": "Success", "rescode": "200"}}
    )
