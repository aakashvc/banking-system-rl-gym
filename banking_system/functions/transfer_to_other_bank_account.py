import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class TransferToOtherBankAccount(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        from_account_id: int,
        beneficiary_id: int,
        amount: float,
        channel: Optional[str] = "ONLINE"
    ) -> str:
        accounts = data.get('accounts', {})
        beneficiaries = data.get('beneficiaries', {})
        transactions = data.get('transactions', {})

        # Validate from_account_id and fetch source account by key
        if not isinstance(from_account_id, int):
            return "Error: 'from_account_id' must be an integer"
        src_key = str(from_account_id)
        source_account = accounts.get(src_key)
        if not source_account:
            return f"Error: Account '{from_account_id}' not found"

        # Validate beneficiary_id
        ben = beneficiaries.get(str(beneficiary_id))
        if not ben:
            return f"Error: Beneficiary '{beneficiary_id}' not found"
        if ben.get('beneficiary_type') != 'BANK_ACCOUNT':
            return "Error: Beneficiary is not a bank account"

        # Validate amount (float)
        try:
            amt = float(amount)
        except (TypeError, ValueError):
            return "Error: 'amount' must be a number"
        if amt <= 0:
            return "Error: 'amount' must be greater than 0"

        # Validate optional channel
        valid_channels = {"BRANCH", "ATM", "ONLINE", "MOBILE"}
        if channel is not None:
            if not isinstance(channel, str):
                return "Error: 'channel' must be a string"
            if channel not in valid_channels:
                return f"Error: 'channel' must be one of: {', '.join(valid_channels)}"
        else:
            channel = "ONLINE"

        # Check sufficient funds
        current_balance = float(source_account.get('balance', 0))
        if amt > current_balance:
            return "Error: Insufficient funds"

        # Deduct from source account
        now_iso = datetime.now().isoformat()
        source_account['balance'] = round(current_balance - amt, 2)
        source_account['updated_at'] = now_iso

        # If the destination (other bank) account exists in our DB by account_number, credit it
        dest_acct_number = ben.get('account_number')
        dest_account = None
        dest_key = None
        if dest_acct_number:
            for k, acc in accounts.items():
                if acc.get('account_number') == dest_acct_number:
                    dest_account = acc
                    dest_key = k
                    break
        if dest_account:
            dest_balance = float(dest_account.get('balance', 0))
            dest_account['balance'] = round(dest_balance + amt, 2)
            dest_account['updated_at'] = now_iso

        # Generate new transaction_id
        existing_ids = [int(tid) for tid in transactions.keys() if tid.isdigit()]
        new_txn_id = str(max(existing_ids) + 1) if existing_ids else "1"

        # Create transaction record (source-side)
        txn = {
            "transaction_id": int(new_txn_id),
            "account_id": from_account_id,
            "type": "TRANSFER",
            "channel": channel,
            "amount": round(amt, 2),
            "occurred_at": now_iso,
            "beneficiary_id": beneficiary_id,
            "card_id": None,
            "merchant": None,
            "card_tx_status": None,
            "created_at": now_iso
        }
        transactions[new_txn_id] = txn

        return json.dumps({
            "message": "Transfer to other bank account successful",
            "transaction": txn
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "transfer_to_other_bank_account",
                "description": "Send funds to a saved bank account beneficiary. If the destination account_number exists in data, credit that account as well.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "from_account_id": {
                            "type": "integer",
                            "description": "ID of the account from which to transfer funds"
                        },
                        "beneficiary_id": {
                            "type": "integer",
                            "description": "ID of the bank account beneficiary"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Amount to transfer (number; decimals allowed)"
                        },
                        "channel": {
                            "type": "string",
                            "description": "Transfer channel (optional; BRANCH, ATM, ONLINE, MOBILE)"
                        }
                    },
                    "required": ["from_account_id", "beneficiary_id", "amount"]
                }
            }
        }
