"""Facade for M-Pesa Account Balance API interactions."""

from mpesa_sdk.auth import TokenManager
from mpesa_sdk.http_client import HttpClient
from mpesa_sdk.account_balance import (
    AccountBalance,
    AccountBalanceRequest,
    AccountBalanceResponse,
)


class BalanceService:
    """Facade for M-Pesa Account Balance operations."""

    def __init__(self, http_client: HttpClient, token_manager: TokenManager) -> None:
        """Initialize the Balance service."""
        self.http_client = http_client
        self.token_manager = token_manager
        self.account_balance = AccountBalance(
            http_client=self.http_client,
            token_manager=self.token_manager,
        )

    def query(
        self,
        initiator: str,
        security_credential: str,
        command_id: str,
        party_a: int,
        identifier_type: int,
        remarks: str,
        result_url: str,
        queue_timeout_url: str,
        **kwargs,
    ) -> AccountBalanceResponse:
        """Query account balance.

        Args:
            initiator: Name of the initiator.
            security_credential: Security credential for authentication.
            command_id: Command ID for the transaction.
            party_a: Shortcode of the account to query.
            identifier_type: Type of identifier for PartyA.
            remarks: Additional remarks.
            result_url: URL for result notification.
            queue_timeout_url: URL for timeout notification.
            **kwargs: Additional fields for AccountBalanceRequest.

        Returns:
            AccountBalanceResponse: Response from the M-Pesa API.
        """
        request = AccountBalanceRequest(
            Initiator=initiator,
            SecurityCredential=security_credential,
            CommandID=command_id,
            PartyA=party_a,
            IdentifierType=identifier_type,
            Remarks=remarks,
            ResultURL=result_url,
            QueueTimeOutURL=queue_timeout_url,
            **{
                k: v
                for k, v in kwargs.items()
                if k in AccountBalanceRequest.model_fields
            },
        )
        return self.account_balance.query(request)
