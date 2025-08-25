"""Facade for M-Pesa Transaction Reversal API interactions."""

from typing import Optional
from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.reversal import (
    Reversal,
    ReversalRequest,
    ReversalResponse,
)


class ReversalService:
    """Facade for M-Pesa Transaction Reversal operations."""

    def __init__(self, http_client: HttpClient, token_manager: TokenManager) -> None:
        """Initialize the Reversal service."""
        self.http_client = http_client
        self.token_manager = token_manager
        self._reversal = Reversal(
            http_client=self.http_client,
            token_manager=self.token_manager,
        )

    def reverse(
        self,
        initiator: str,
        security_credential: str,
        transaction_id: str,
        amount: int,
        receiver_party: int,
        result_url: str,
        queue_timeout_url: str,
        remarks: str,
        occasion: Optional[str] = None,
        **kwargs,
    ) -> ReversalResponse:
        """Initiate a transaction reversal.

        Args:
            initiator: Username used to initiate the request.
            security_credential: Encrypted security credential.
            transaction_id: Mpesa Transaction ID to reverse.
            amount: Amount to reverse (in KES).
            receiver_party: Organization shortcode (6-9 digits).
            result_url: URL for result notifications.
            queue_timeout_url: URL for timeout notifications.
            remarks: Comments for the transaction (max 100 chars).
            occasion: Optional parameter (max 100 chars).
            **kwargs: Additional fields for ReversalRequest.

        Returns:
            ReversalResponse: Response from the M-Pesa API.
        """
        request = ReversalRequest(
            Initiator=initiator,
            SecurityCredential=security_credential,
            TransactionID=transaction_id,
            Amount=amount,
            ReceiverParty=receiver_party,
            ResultURL=result_url,
            QueueTimeOutURL=queue_timeout_url,
            Remarks=remarks,
            Occasion=occasion,
            **{k: v for k, v in kwargs.items() if k in ReversalRequest.model_fields},
        )
        return self._reversal.reverse(request)
