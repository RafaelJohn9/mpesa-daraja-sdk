"""Facade for M-Pesa Dynamic QR Code generation service."""

from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client.mpesa_http_client import HttpClient
from mpesa_sdk.dynamic_qr_code import (
    DynamicQRGenerateRequest,
    DynamicQRGenerateResponse,
    DynamicQRCode,
)


class DynamicQRCodeService:
    """Facade for M-Pesa Dynamic QR Code generation."""

    def __init__(self, http_client: HttpClient, token_manager: TokenManager) -> None:
        """Initialize the Dynamic QR Code service."""
        self.http_client = http_client
        self.token_manager = token_manager
        self.qr_code = DynamicQRCode(
            http_client=self.http_client,
            token_manager=self.token_manager,
        )

    def generate(
        self,
        merchant_name: str,
        ref_no: str,
        amount: float,
        trx_code: str,
        cpi: str,
        size: str,
        **kwargs,
    ) -> DynamicQRGenerateResponse:
        """Generate a dynamic QR code for payment.

        Args:
            merchant_name: Name of the merchant.
            ref_no: Reference number for the transaction.
            amount: Transaction amount.
            trx_code: Transaction type (DynamicQRTransactionType).
            cpi: CPI code.
            size: Size of the QR code.
            **kwargs: Additional fields for DynamicQRGenerateRequest.

        Returns:
            Response DynamicQRGenerateResponse containing QR code details.
        """
        request = DynamicQRGenerateRequest(
            MerchantName=merchant_name,
            RefNo=ref_no,
            Amount=amount,
            TrxCode=trx_code,
            CPI=cpi,
            Size=size,
            **{
                k: v
                for k, v in kwargs.items()
                if k in DynamicQRGenerateRequest.model_fields
            },
        )
        return self.qr_code.generate(request)
