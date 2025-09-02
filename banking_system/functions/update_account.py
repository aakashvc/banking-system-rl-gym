import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class UpdateAccount(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        account_id: int,
        branch_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        account_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        accounts = data.get('accounts', {})

        # Validate account_id
        try:
            aid = int(account_id)
        except (ValueError, TypeError):
            return "Error: 'account_id' must be an integer"

        # Locate the account
        account_key = None
        for key in accounts:
            try:
                if int(key) == aid:
                    account_key = key
                    break
            except:
                continue
        if account_key is None:
            return f"Error: Account '{aid}' not found"

        account = accounts[account_key]

        # Apply updates
        if branch_id is not None:
            if not isinstance(branch_id, int):
                return "Error: 'branch_id' must be an integer"
            account['branch_id'] = branch_id

        if customer_id is not None:
            if not isinstance(customer_id, int):
                return "Error: 'customer_id' must be an integer"
            account['customer_id'] = customer_id

        if account_type is not None:
            if not isinstance(account_type, str):
                return "Error: 'account_type' must be a string"
            account['type'] = account_type

        if status is not None:
            if not isinstance(status, str):
                return "Error: 'status' must be a string"
            account['status'] = status

        # Update timestamp
        account['updated_at'] = datetime.now().isoformat()

        return json.dumps(account, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_account",
                "description": "Modify one or more properties of an account",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "integer",
                            "description": "ID of the account to update"
                        },
                        "branch_id": {
                            "type": "integer",
                            "description": "New branch ID (exact match)"
                        },
                        "customer_id": {
                            "type": "integer",
                            "description": "New customer ID (exact match)"
                        },
                        "account_type": {
                            "type": "string",
                            "description": "New account type (SAVINGS, CHECKING, BUSINESS)"
                        },
                        "status": {
                            "type": "string",
                            "description": "New account status (OPEN, CLOSED, FROZEN)"
                        }
                    },
                    "required": ["account_id"]
                }
            }
        }
