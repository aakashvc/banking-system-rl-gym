import json
from typing import Any, Dict
from src.classes.function import Function
from datetime import datetime


class CreateAccount(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        branch_id: int,
        customer_id: int,
        account_type: str,
        initial_deposit: int
    ) -> str:
        accounts = data.get('accounts', {})

        # Validate inputs
        if not isinstance(branch_id, int):
            return "Error: 'branch_id' must be an integer"
        if not isinstance(customer_id, int):
            return "Error: 'customer_id' must be an integer"
        if not isinstance(account_type, str):
            return "Error: 'account_type' must be a string"
        if not isinstance(initial_deposit, int):
            return "Error: 'initial_deposit' must be an integer"

        # Generate new account_id
        existing_ids = [int(aid) for aid in accounts.keys() if aid.isdigit()]
        new_id_int = max(existing_ids) + 1 if existing_ids else 1
        new_id = str(new_id_int)

        now = datetime.now()
        opened_date = now.date().isoformat()
        now_str = now.isoformat()

        # Generate account_number: one more than the last account's number
        prev_id = new_id_int - 1
        prev_key = str(prev_id)
        if prev_key in accounts:
            prev_acc_num_str = accounts[prev_key].get('account_number', '')
            try:
                prev_acc_int = int(prev_acc_num_str)
                account_number = str(prev_acc_int + 1)
            except (ValueError, TypeError):
                account_number = str(new_id_int)
        else:
            # No previous account, initialize with new_id
            account_number = str(new_id_int)

        account = {
            "account_id": new_id_int,
            "branch_id": branch_id,
            "customer_id": customer_id,
            "account_number": account_number,
            "type": account_type,
            "balance": float(initial_deposit),
            "opened_date": opened_date,
            "status": "OPEN",
            "created_at": now_str,
            "updated_at": now_str
        }

        accounts[new_id] = account

        return json.dumps({
            "message": "Account created successfully",
            "account": account
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_account",
                "description": "Open a new account with an initial deposit; account_number is set to one more than the previous account's number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_id": {
                            "type": "integer",
                            "description": "Branch ID where the account is opened"
                        },
                        "customer_id": {
                            "type": "integer",
                            "description": "Customer ID for the new account"
                        },
                        "account_type": {
                            "type": "string",
                            "description": "Type of account (e.g., SAVINGS, CHECKING, BUSINESS)"
                        },
                        "initial_deposit": {
                            "type": "integer",
                            "description": "Initial deposit amount for the new account"
                        }
                    },
                    "required": ["branch_id", "customer_id", "account_type", "initial_deposit"]
                }
            }
        }
