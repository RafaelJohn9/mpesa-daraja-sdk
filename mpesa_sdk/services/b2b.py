"""Facade for M-Pesa B2B APIs (Express Checkout)."""

from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.B2B_express_checkout import (
    B2BExpressCheckout,
    B2BExpressCheckoutRequest,
    B2BExpressCheckoutResponse,
)


class B2BService:
    """Facade for all M-Pesa B2B APIs."""

    def __init__(self, http_client: HttpClient, token_manager: TokenManager) -> None:
        """Initialize the B2B service facade."""
        self.http_client = http_client
        self.token_manager = token_manager
        self.express_checkout = B2BExpressCheckout(
            http_client=self.http_client, token_manager=self.token_manager
        )

    def express_checkout(
        self,
        primary_short_code: str,
        receiver_short_code: str,
        amount: int,
        payment_ref: str,
        callback_url: str,
        partner_name: str,
        request_ref_id: str,
        **kwargs,
    ) -> B2BExpressCheckoutResponse:
        """Initiate a B2B Express Checkout USSD Push transaction.

        Args:
            primary_short_code: The primary short code for the transaction.
            receiver_short_code: The receiver short code for the transaction.
            amount: The amount to be transacted.
            payment_ref: Reference for the payment.
            callback_url: URL for receiving the callback.
            partner_name: Name of the partner.
            request_ref_id: Unique reference ID for the request.
            kwargs: Fields for B2BExpressCheckoutRequest.

        Returns:
            B2BExpressCheckoutResponse: Response from M-Pesa API.
        """
        request = B2BExpressCheckoutRequest(
            primaryShortCode=primary_short_code,
            receiverShortCode=receiver_short_code,
            amount=amount,
            paymentRef=payment_ref,
            callbackUrl=callback_url,
            partnerName=partner_name,
            RequestRefID=request_ref_id,
            **{
                k: v
                for k, v in kwargs.items()
                if k in B2BExpressCheckoutRequest.model_fields
            },
        )
        return self.express_checkout.ussd_push(request)
