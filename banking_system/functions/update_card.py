import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class UpdateCard(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        card_id: int,
        credit_limit: Optional[int] = None,
        status: Optional[str] = None,
        expiry_date: Optional[str] = None
    ) -> str:
        cards = data.get('cards', {})

        # Validate card_id
        if not isinstance(card_id, int):
            return "Error: 'card_id' must be an integer"

        # Locate card
        card_key = None
        for cid in cards:
            try:
                if int(cid) == card_id:
                    card_key = cid
                    break
            except (ValueError, TypeError):
                continue
        if card_key is None:
            return f"Error: Card '{card_id}' not found"
        card = cards[card_key]

        # Update credit_limit if provided
        if credit_limit is not None:
            if not isinstance(credit_limit, int) or credit_limit < 0:
                return "Error: 'credit_limit' must be a non-negative integer"
            card['credit_limit'] = credit_limit

        # Update status if provided
        if status is not None:
            if not isinstance(status, str):
                return "Error: 'status' must be a string"
            valid_statuses = {"ACTIVE", "BLOCKED", "EXPIRED"}
            if status not in valid_statuses:
                return f"Error: 'status' must be one of: {', '.join(valid_statuses)}"
            card['status'] = status

        # Update expiry_date if provided
        if expiry_date is not None:
            if not isinstance(expiry_date, str):
                return "Error: 'expiry_date' must be a string in YYYY-MM-DD format"
            try:
                exp = datetime.fromisoformat(expiry_date).date()
                card['expiry_date'] = exp.isoformat()
            except Exception:
                return "Error: 'expiry_date' must be a string in YYYY-MM-DD format"

        # Update timestamp
        card['updated_at'] = datetime.now().isoformat()

        return json.dumps(card, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_card",
                "description": "Modify properties of an existing card (credit limit, status, expiry date)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "card_id": {
                            "type": "integer",
                            "description": "ID of the card to update"
                        },
                        "credit_limit": {
                            "type": "integer",
                            "description": "New credit limit (non-negative integer)"
                        },
                        "status": {
                            "type": "string",
                            "description": "New card status (ACTIVE, BLOCKED, EXPIRED)"
                        },
                        "expiry_date": {
                            "type": "string",
                            "format": "date",
                            "description": "New expiry date (YYYY-MM-DD)"
                        }
                    },
                    "required": ["card_id"]
                }
            }
        }
