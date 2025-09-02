import json
from typing import Any, Dict
from src.classes.function import Function
from datetime import datetime


class WithdrawFromAccount(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        account_id: int,
        amount: float,
        channel: str
    ) -> str:
        accounts = data.get('accounts', {})
        transactions = data.get('transactions', {})

        # Validate account_id and fetch account directly by key
        if not isinstance(account_id, int):
            return "Error: 'account_id' must be an integer"
        acct_key = str(account_id)
        account = accounts.get(acct_key)
        if not account:
            return f"Error: Account '{account_id}' not found"

        # Validate amount (float allowed)
        if not isinstance(amount, (int, float)):
            return "Error: 'amount' must be a number"
        amount_val = float(amount)
        if amount_val <= 0:
            return "Error: 'amount' must be greater than 0"

        # Validate channel
        if not isinstance(channel, str):
            return "Error: 'channel' must be a string"
        valid_channels = {"BRANCH", "ATM", "ONLINE", "MOBILE"}
        if channel not in valid_channels:
            return f"Error: 'channel' must be one of: {', '.join(valid_channels)}"

        # Check sufficient funds
        current_balance = float(account.get('balance', 0))
        if amount_val > current_balance:
            return "Error: Insufficient funds"

        # Update account balance (store as float with 2 decimals)
        new_balance = round(current_balance - amount_val, 2)
        account['balance'] = new_balance
        account['updated_at'] = datetime.now().isoformat()

        # Generate new transaction_id
        existing_ids = [int(tid) for tid in transactions.keys() if tid.isdigit()]
        new_txn_id = str(max(existing_ids) + 1) if existing_ids else "1"

        now = datetime.now().isoformat()

        # Create transaction record
        txn = {
            "transaction_id": int(new_txn_id),
            "account_id": account_id,
            "type": "WITHDRAWAL",
            "channel": channel,
            "amount": round(amount_val, 2),
            "occurred_at": now,
            "beneficiary_id": None,
            "card_id": None,
            "merchant": None,
            "card_tx_status": None,
            "created_at": now
        }
        transactions[new_txn_id] = txn

        return json.dumps({
            "message": "Withdrawal successful",
            "transaction": txn
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "withdraw_from_account",
                "description": "Withdraw funds from an account with overdraft/limits checking",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "integer",
                            "description": "ID of the account to withdraw from"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Amount to withdraw (number; decimals allowed)"
                        },
                        "channel": {
                            "type": "string",
                            "description": "Channel of the withdrawal (BRANCH, ATM, ONLINE, MOBILE)"
                        }
                    },
                    "required": ["account_id", "amount", "channel"]
                }
            }
        }
