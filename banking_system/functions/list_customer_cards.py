import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListCustomerCards(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        card_id: Optional[int] = None,
        account_id: Optional[int] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
        balance_min: Optional[int] = None,
        balance_max: Optional[int] = None,
        credit_limit_min: Optional[int] = None,
        credit_limit_max: Optional[int] = None
    ) -> str:
        cards = data.get('cards', {})
        results = []

        for cid, card in cards.items():
            # Filter by card_id (exact)
            if card_id is not None:
                try:
                    if int(cid) != card_id:
                        continue
                except (ValueError, TypeError):
                    continue

            # Filter by account_id (exact)
            if account_id is not None and card.get('account_id') != account_id:
                continue

            # Filter by type (exact, case-insensitive)
            if type and card.get('type', '').lower() != type.lower():
                continue

            # Filter by status (exact, case-insensitive)
            if status and card.get('status', '').lower() != status.lower():
                continue

            # Filter by balance range
            bal = card.get('balance', 0)
            if balance_min is not None and bal < balance_min:
                continue
            if balance_max is not None and bal > balance_max:
                continue

            # Filter by credit limit range
            limit = card.get('credit_limit', 0)
            if credit_limit_min is not None and limit < credit_limit_min:
                continue
            if credit_limit_max is not None and limit > credit_limit_max:
                continue

            results.append(card)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_customer_cards",
                "description": "List or filter all cards for a customer by various fields",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "card_id": {
                            "type": "integer",
                            "description": "Card ID to filter by (exact match)"
                        },
                        "account_id": {
                            "type": "integer",
                            "description": "Account ID to filter by (exact match)"
                        },
                        "type": {
                            "type": "string",
                            "description": "Card type (DEBIT, CREDIT, PREPAID)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Card status (ACTIVE, BLOCKED, EXPIRED)"
                        },
                        "balance_min": {
                            "type": "integer",
                            "description": "Minimum card balance (inclusive)"
                        },
                        "balance_max": {
                            "type": "integer",
                            "description": "Maximum card balance (inclusive)"
                        },
                        "credit_limit_min": {
                            "type": "integer",
                            "description": "Minimum credit limit (inclusive)"
                        },
                        "credit_limit_max": {
                            "type": "integer",
                            "description": "Maximum credit limit (inclusive)"
                        }
                    },
                    "required": []
                }
            }
        }
