"""Facade for M-PESA Bill Manager API interactions."""

from typing import Optional, List
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.bill_manager import (
    BillManager,
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
    InvoiceItem,
)


class BillService:
    """Facade for M-PESA Bill Manager operations."""

    def __init__(
        self,
        http_client: HttpClient,
        token_manager: TokenManager,
        app_key: Optional[str] = None,
    ) -> None:
        """Initialize the Bill service."""
        self.http_client = http_client
        self.token_manager = token_manager
        self.bill_manager = BillManager(
            http_client=self.http_client,
            token_manager=self.token_manager,
            app_key=app_key,
        )

    def opt_in(
        self,
        shortcode: int,
        email: str,
        official_contact: str,
        send_reminders: int,
        logo: Optional[str],
        callback_url: str,
    ) -> BillManagerOptInResponse:
        """Onboard a paybill to Bill Manager."""
        request = BillManagerOptInRequest(
            shortcode=shortcode,
            email=email,
            officialContact=official_contact,
            sendReminders=send_reminders,
            logo=logo,
            callbackurl=callback_url,
        )
        return self.bill_manager.opt_in(request)

    def update_opt_in(
        self,
        shortcode: int,
        email: str,
        official_contact: str,
        send_reminders: int,
        logo: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> BillManagerUpdateOptInResponse:
        """Update opt-in details for Bill Manager."""
        request = BillManagerUpdateOptInRequest(
            shortcode=shortcode,
            email=email,
            officialContact=official_contact,
            sendReminders=send_reminders,
            logo=logo,
            callbackurl=callback_url,
        )
        return self.bill_manager.update_opt_in(request)

    def send_single_invoice(
        self,
        external_reference: str,
        billed_full_name: str,
        billed_phone_number: str,
        billed_period: str,
        invoice_name: str,
        due_date: str,
        account_reference: str,
        amount: int,
        invoice_items: Optional[List[InvoiceItem]] = None,
    ) -> BillManagerSingleInvoiceResponse:
        """Send a single invoice via Bill Manager."""
        request = BillManagerSingleInvoiceRequest(
            externalReference=external_reference,
            billedFullName=billed_full_name,
            billedPhoneNumber=billed_phone_number,
            billedPeriod=billed_period,
            invoiceName=invoice_name,
            dueDate=due_date,
            accountReference=account_reference,
            amount=amount,
            invoiceItems=invoice_items,
        )
        return self.bill_manager.send_single_invoice(request)

    def send_bulk_invoice(
        self,
        invoices: List[BillManagerSingleInvoiceRequest],
    ) -> BillManagerBulkInvoiceResponse:
        """Send multiple invoices via Bill Manager."""
        request = BillManagerBulkInvoiceRequest(invoices=invoices)
        return self.bill_manager.send_bulk_invoice(request)

    def cancel_single_invoice(
        self,
        external_reference: str,
    ) -> BillManagerCancelInvoiceResponse:
        """Cancel a single invoice via Bill Manager."""
        request = BillManagerCancelSingleInvoiceRequest(
            externalReference=external_reference
        )
        return self.bill_manager.cancel_single_invoice(request)

    def cancel_bulk_invoice(
        self,
        external_references: List[str],
    ) -> BillManagerCancelInvoiceResponse:
        """Cancel multiple invoices via Bill Manager."""
        invoice_requests = [
            BillManagerCancelSingleInvoiceRequest(externalReference=ref)
            for ref in external_references
        ]
        request = BillManagerCancelBulkInvoiceRequest(invoices=invoice_requests)
        return self.bill_manager.cancel_bulk_invoice(request)
