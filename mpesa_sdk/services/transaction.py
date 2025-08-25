"""Facade for M-Pesa Transaction Status API interactions."""

from typing import Optional

from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.transaction_status import (
    TransactionStatus,
    TransactionStatusRequest,
    TransactionStatusResponse,
)


class TransactionService:
    """Facade for M-Pesa Transaction Status operations."""

    def __init__(self, http_client: HttpClient, token_manager: TokenManager) -> None:
        """Initialize the Transaction service."""
        self.http_client = http_client
        self.token_manager = token_manager
        self.transaction_status = TransactionStatus(
            http_client=self.http_client,
            token_manager=self.token_manager,
        )

    def query_status(
        self,
        initiator: str,
        security_credential: str,
        command_id: str,
        transaction_id: str,
        party_a: int,
        identifier_type: int,
        result_url: str,
        queue_timeout_url: str,
        remarks: str = "",
        occasion: str = "",
        originator_conversation_id: Optional[str] = None,
        **kwargs,
    ) -> TransactionStatusResponse:
        """Query the status of a transaction.

        Args:
            initiator: Name of the initiator.
            security_credential: Security credential for authentication.
            command_id: Command ID for the transaction.
            transaction_id: Unique transaction ID.
            party_a: Party A identifier.
            identifier_type: Type of identifier.
            result_url: URL for result notification.
            queue_timeout_url: URL for timeout notification.
            remarks: Additional remarks.
            occasion: Occasion for the transaction.
            originator_conversation_id: Can be used to query if you don't have the transaction ID.
            **kwargs: Additional fields for TransactionStatusRequest.

        Returns:
            TransactionStatusResponse: Response from the M-Pesa API.
        """
        request = TransactionStatusRequest(
            Initiator=initiator,
            SecurityCredential=security_credential,
            CommandID=command_id,
            TransactionID=transaction_id,
            PartyA=party_a,
            IdentifierType=identifier_type,
            ResultURL=result_url,
            QueueTimeOutURL=queue_timeout_url,
            Remarks=remarks,
            Occasion=occasion,
            OriginatorConversationID=originator_conversation_id,
            **{
                k: v
                for k, v in kwargs.items()
                if k in TransactionStatusRequest.model_fields
            },
        )
        return self.transaction_status.query(request)
