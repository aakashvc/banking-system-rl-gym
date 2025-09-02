import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListAccountTransactions(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        transaction_id: Optional[int] = None,
        account_id: Optional[int] = None,
        type: Optional[str] = None,
        channel: Optional[str] = None,
        amount_min: Optional[float] = None,
        amount_max: Optional[float] = None,
        occurred_from: Optional[str] = None,
        occurred_to: Optional[str] = None,
        beneficiary_id: Optional[int] = None,
        card_id: Optional[int] = None,
        merchant: Optional[str] = None,
        card_tx_status: Optional[str] = None
    ) -> str:
        transactions = data.get('transactions', {})
        results = []

        merchant_lower = merchant.lower() if merchant else None

        # Parse occurred_from/to ISO strings into datetimes
        occ_from_dt: Optional[datetime] = None
        occ_to_dt: Optional[datetime] = None
        if occurred_from:
            try:
                occ_from_dt = datetime.fromisoformat(occurred_from)
            except ValueError:
                return "Error: 'occurred_from' must be an ISO datetime string"
        if occurred_to:
            try:
                occ_to_dt = datetime.fromisoformat(occurred_to)
            except ValueError:
                return "Error: 'occurred_to' must be an ISO datetime string"

        def parse_date(t: Dict[str, Any]) -> datetime:
            occ = t.get('occurred_at')
            if isinstance(occ, str):
                try:
                    return datetime.fromisoformat(occ)
                except ValueError:
                    pass
            if isinstance(occ, datetime):
                return occ
            return datetime.min

        for txn in transactions.values():
            if transaction_id is not None and txn.get('transaction_id') != transaction_id:
                continue
            if account_id is not None and txn.get('account_id') != account_id:
                continue
            if type and txn.get('type') != type:
                continue
            if channel and txn.get('channel') != channel:
                continue

            # Amount range (floats allowed)
            amt = txn.get('amount')
            try:
                amt_val = float(amt)
            except (TypeError, ValueError):
                # If amount is not numeric, skip this txn
                continue
            if amount_min is not None and amt_val < float(amount_min):
                continue
            if amount_max is not None and amt_val > float(amount_max):
                continue

            occ_dt = parse_date(txn)
            if occ_from_dt and occ_dt < occ_from_dt:
                continue
            if occ_to_dt and occ_dt > occ_to_dt:
                continue

            if beneficiary_id is not None and txn.get('beneficiary_id') != beneficiary_id:
                continue
            if card_id is not None and txn.get('card_id') != card_id:
                continue

            if merchant_lower and merchant_lower not in (txn.get('merchant') or '').lower():
                continue
            if card_tx_status and txn.get('card_tx_status') != card_tx_status:
                continue

            results.append(txn)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_account_transactions",
                "description": "Paginate or filter an account’s transactions by any field",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transaction_id": {
                            "type": "integer",
                            "description": "Transaction ID to filter by (exact match)"
                        },
                        "account_id": {
                            "type": "integer",
                            "description": "Account ID to filter by (exact match)"
                        },
                        "type": {
                            "type": "string",
                            "description": "Transaction type (exact match: DEPOSIT, WITHDRAWAL, TRANSFER, PAYMENT, CARD_PURCHASE)"
                        },
                        "channel": {
                            "type": "string",
                            "description": "Transaction channel (exact match: BRANCH, ATM, ONLINE, MOBILE, POS)"
                        },
                        "amount_min": {
                            "type": "number",
                            "description": "Minimum transaction amount (inclusive; decimals allowed)"
                        },
                        "amount_max": {
                            "type": "number",
                            "description": "Maximum transaction amount (inclusive; decimals allowed)"
                        },
                        "occurred_from": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Earliest occurred_at datetime as ISO string (inclusive)"
                        },
                        "occurred_to": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Latest occurred_at datetime as ISO string (inclusive)"
                        },
                        "beneficiary_id": {
                            "type": "integer",
                            "description": "Beneficiary ID to filter by (exact match)"
                        },
                        "card_id": {
                            "type": "integer",
                            "description": "Card ID to filter by (exact match)"
                        },
                        "merchant": {
                            "type": "string",
                            "description": "Partial or full merchant name (case-insensitive substring match)"
                        },
                        "card_tx_status": {
                            "type": "string",
                            "description": "Card transaction status (exact match: UNBILLED, BILLED)"
                        }
                    },
                    "required": []
                }
            }
        }
