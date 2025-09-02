import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListCustomerAccounts(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        account_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        branch_id: Optional[int] = None,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        balance_min: Optional[int] = None,
        balance_max: Optional[int] = None
    ) -> str:
        accounts = data.get('accounts', {})
        results = []

        for aid, acc in accounts.items():
            # Filter by account_id (exact)
            if account_id is not None:
                try:
                    if int(aid) != account_id:
                        continue
                except (ValueError, TypeError):
                    continue

            # Filter by customer_id (exact)
            if customer_id is not None and acc.get('customer_id') != customer_id:
                continue

            # Filter by branch_id (exact)
            if branch_id is not None and acc.get('branch_id') != branch_id:
                continue

            # Filter by account_type (exact, case-insensitive)
            if account_type and acc.get('type', '').lower() != account_type.lower():
                continue

            # Filter by status (exact, case-insensitive)
            if status and acc.get('status', '').lower() != status.lower():
                continue

            # Filter by balance_min (exact integer comparison)
            if balance_min is not None:
                try:
                    if int(acc.get('balance', 0)) < balance_min:
                        continue
                except (TypeError, ValueError):
                    continue

            # Filter by balance_max (exact integer comparison)
            if balance_max is not None:
                try:
                    if int(acc.get('balance', 0)) > balance_max:
                        continue
                except (TypeError, ValueError):
                    continue

            results.append(acc)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_customer_accounts",
                "description": "List or filter all accounts for a customer by various fields",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "integer",
                            "description": "Account ID to filter by (exact match)"
                        },
                        "customer_id": {
                            "type": "integer",
                            "description": "Customer ID to filter by (exact match)"
                        },
                        "branch_id": {
                            "type": "integer",
                            "description": "Branch ID to filter by (exact match)"
                        },
                        "account_type": {
                            "type": "string",
                            "description": "Account type (SAVINGS, CHECKING, BUSINESS)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Account status (OPEN, CLOSED, FROZEN)"
                        },
                        "balance_min": {
                            "type": "integer",
                            "description": "Minimum account balance (inclusive, integer)"
                        },
                        "balance_max": {
                            "type": "integer",
                            "description": "Maximum account balance (inclusive, integer)"
                        }
                    },
                    "required": []
                }
            }
        }
