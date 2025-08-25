"""Facade for M-Pesa B2B APIs (Express Checkout)."""

from typing import Optional
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.business_buy_goods import (
    BusinessBuyGoods,
    BusinessBuyGoodsRequest,
    BusinessBuyGoodsResponse,
)
from mpesa_sdk.business_paybill import (
    BusinessPayBill,
    BusinessPayBillRequest,
    BusinessPayBillResponse,
)
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
        self._express_checkout = B2BExpressCheckout(
            http_client=self.http_client, token_manager=self.token_manager
        )
        self._business_paybill = BusinessPayBill(
            http_client=self.http_client,
            token_manager=self.token_manager,
        )
        self._business_buygoods = BusinessBuyGoods(
            http_client=self.http_client,
            token_manager=self.token_manager,
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
        """Initiate a B2B Express Checkout USSD Push transaction to another merchant.

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
        return self._express_checkout.ussd_push(request)

    def paybill(
        self,
        initiator: str,
        security_credential: str,
        amount: int,
        party_a: int,
        party_b: int,
        account_reference: str,
        requester: str,
        remarks: str,
        queue_timeout_url: str,
        result_url: str,
        **kwargs,
    ) -> BusinessPayBillResponse:
        """Initiate a Business PayBill transaction to another merchant.

        Args:
            initiator: API username.
            security_credential: Encrypted credential.
            amount: The amount to be transacted.
            party_a: The sender short code.
            party_b: The receiver short code.
            account_reference: Reference for the account.
            requester: Requester phone number.
            remarks: Remarks for the transaction.
            queue_timeout_url: URL for timeout callback.
            result_url: URL for result callback.
            kwargs: Additional fields for BusinessPayBillRequest.

        Returns:
            BusinessPayBillResponse: Response from M-Pesa API.
        """
        request = BusinessPayBillRequest(
            Initiator=initiator,
            SecurityCredential=security_credential,
            Amount=amount,
            PartyA=party_a,
            PartyB=party_b,
            AccountReference=account_reference,
            Requester=requester,
            Remarks=remarks,
            QueueTimeOutURL=queue_timeout_url,
            ResultURL=result_url,
            **{
                k: v
                for k, v in kwargs.items()
                if k in BusinessPayBillRequest.model_fields
            },
        )

        return self._business_paybill.paybill(request)

    def buygoods(
        self,
        initiator: str,
        security_credential: str,
        amount: int,
        party_a: int,
        party_b: int,
        account_reference: str,
        requester: str,
        remarks: str,
        queue_timeout_url: str,
        result_url: str,
        occassion: Optional[str] = None,
        **kwargs,
    ) -> BusinessBuyGoodsResponse:
        """Initiate a Business Buy Goods transaction to another merchant.

        Args:
            initiator: API username.
            security_credential: Encrypted credential.
            amount: The amount to be transacted.
            party_a: The sender short code.
            party_b: The receiver short code.
            account_reference: Reference for the account.
            requester: Requester phone number.
            remarks: Remarks for the transaction.
            queue_timeout_url: URL for timeout callback.
            result_url: URL for result callback.
            occassion: Optional transaction occasion.
            kwargs: Additional fields for BusinessBuyGoodsRequest.

        Returns:
            BusinessBuyGoodsResponse: Response from M-Pesa API.
        """
        request = BusinessBuyGoodsRequest(
            Initiator=initiator,
            SecurityCredential=security_credential,
            Amount=amount,
            PartyA=party_a,
            PartyB=party_b,
            AccountReference=account_reference,
            Requester=requester,
            Remarks=remarks,
            QueueTimeOutURL=queue_timeout_url,
            ResultURL=result_url,
            Occassion=occassion,
            **{
                k: v
                for k, v in kwargs.items()
                if k in BusinessBuyGoodsRequest.model_fields
            },
        )
        return self._business_buygoods.buy_goods(request)
