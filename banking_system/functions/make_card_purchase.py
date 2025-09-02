import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class MakeCardPurchase(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        card_id: int,
        amount: float,
        merchant: str,
        channel: Optional[str] = 'POS'
    ) -> str:
        cards = data.get('cards', {})
        transactions = data.get('transactions', {})
        accounts = data.get('accounts', {})

        # Validate card_id and fetch card directly by key
        key = str(card_id)
        card = cards.get(key)
        if not card:
            return f"Error: Card '{card_id}' not found"

        # Validate amount (float allowed)
        if not isinstance(amount, (int, float)):
            return "Error: 'amount' must be a number"
        amount = float(amount)
        if amount <= 0:
            return "Error: 'amount' must be greater than 0"

        # Validate merchant
        if not isinstance(merchant, str) or not merchant.strip():
            return "Error: 'merchant' must be a non-empty string"

        # Validate channel
        if channel is not None and not isinstance(channel, str):
            return "Error: 'channel' must be a string"
        valid_channels = {"BRANCH", "ATM", "ONLINE", "MOBILE", "POS"}
        if channel not in valid_channels:
            return f"Error: 'channel' must be one of: {', '.join(valid_channels)}"

        ctype = card.get('type')
        now_iso = datetime.now().isoformat()

        # CREDIT card: decrease available credit_limit by amount (cannot go below 0)
        if ctype == 'CREDIT':
            credit_limit = float(card.get('credit_limit', 0))
            if credit_limit - amount < 0:
                return "Error: Credit limit exceeded"
            card['credit_limit'] = round(credit_limit - amount, 2)
            card['updated_at'] = now_iso

        # PREPAID card: deduct from the card's own balance
        elif ctype == 'PREPAID':
            current_balance = float(card.get('balance', 0))
            if amount > current_balance:
                return "Error: Insufficient prepaid card balance"
            card['balance'] = round(current_balance - amount, 2)
            card['updated_at'] = now_iso

        # DEBIT card: deduct from the linked bank account
        elif ctype == 'DEBIT':
            linked_account_key = str(card.get('account_id'))
            account = accounts.get(linked_account_key)
            if not account:
                return f"Error: Linked account '{card.get('account_id')}' not found"
            acct_balance = float(account.get('balance', 0))
            if amount > acct_balance:
                return "Error: Insufficient funds in linked account"
            account['balance'] = round(acct_balance - amount, 2)
            account['updated_at'] = now_iso

        else:
            return f"Error: Unsupported card type '{ctype}'"

        # Generate new transaction_id
        existing_ids = [int(tid) for tid in transactions.keys() if tid.isdigit()]
        new_txn_id = str(max(existing_ids) + 1) if existing_ids else "1"

        # Create transaction record
        txn = {
            "transaction_id": int(new_txn_id),
            "account_id": card.get('account_id'),
            "type": "CARD_PURCHASE",
            "channel": channel,
            "amount": round(amount, 2),
            "occurred_at": now_iso,
            "beneficiary_id": None,
            "card_id": card_id,
            "merchant": merchant,
            "card_tx_status": "UNBILLED",
            "created_at": now_iso
        }
        transactions[new_txn_id] = txn

        return json.dumps({
            "message": "Card purchase recorded",
            "transaction": txn
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "make_card_purchase",
                "description": "Record a POS or online purchase on a card (credit: checks/decreases available limit; prepaid: deducts card balance; debit: deducts linked account balance)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "card_id": {
                            "type": "integer",
                            "description": "ID of the card used for purchase"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Purchase amount (number; decimals allowed)"
                        },
                        "merchant": {
                            "type": "string",
                            "description": "Merchant name for the purchase"
                        },
                        "channel": {
                            "type": "string",
                            "description": "Channel of the purchase (BRANCH, ATM, ONLINE, MOBILE, POS)"
                        }
                    },
                    "required": ["card_id", "amount", "merchant"]
                }
            }
        }
