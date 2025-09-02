import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListCardTransactions(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        card_id: Optional[int] = None,
        type: Optional[str] = None,
        channel: Optional[str] = None,
        amount_min: Optional[int] = None,
        amount_max: Optional[int] = None,
        occurred_from: Optional[str] = None,
        occurred_to: Optional[str] = None,
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
            # Filter by card_id (exact)
            if card_id is not None and txn.get('card_id') != card_id:
                continue

            # Filter by type (exact)
            if type and txn.get('type') != type:
                continue

            # Filter by channel (exact)
            if channel and txn.get('channel') != channel:
                continue

            # Filter by amount range
            amt = txn.get('amount')
            if amount_min is not None and amt < amount_min:
                continue
            if amount_max is not None and amt > amount_max:
                continue

            # Filter by occurred_at range
            occ_dt = parse_date(txn)
            if occ_from_dt and occ_dt < occ_from_dt:
                continue
            if occ_to_dt and occ_dt > occ_to_dt:
                continue

            # Partial, case-insensitive match on merchant
            if merchant_lower and merchant_lower not in (txn.get('merchant') or '').lower():
                continue

            # Filter by card_tx_status (exact)
            if card_tx_status and txn.get('card_tx_status') != card_tx_status:
                continue

            results.append(txn)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_card_transactions",
                "description": "List or filter transactions on a card by various fields",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "card_id": {
                            "type": "integer",
                            "description": "Card ID to filter by (exact match)"
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
                            "type": "integer",
                            "description": "Minimum transaction amount (inclusive, integer)"
                        },
                        "amount_max": {
                            "type": "integer",
                            "description": "Maximum transaction amount (inclusive, integer)"
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
