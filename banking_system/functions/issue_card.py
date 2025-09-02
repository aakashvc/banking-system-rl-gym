import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class IssueCard(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        account_id: int,
        card_type: str,
        expiry_date: str,
        credit_limit: Optional[int] = None,
        balance: Optional[int] = None
    ) -> str:
        accounts = data.get('accounts', {})
        cards = data.get('cards', {})

        # Validate account_id
        key = str(account_id)
        if key not in accounts:
            return f"Error: Account '{account_id}' not found"

        # Validate card_type
        if card_type not in {"DEBIT", "CREDIT", "PREPAID"}:
            return "Error: 'card_type' must be one of: DEBIT, CREDIT, PREPAID"

        # Validate expiry_date
        try:
            exp_date = datetime.fromisoformat(expiry_date).date().isoformat()
        except Exception:
            return "Error: 'expiry_date' must be YYYY-MM-DD"

        # For CREDIT cards, require credit_limit
        if card_type == "CREDIT":
            if credit_limit is None or credit_limit < 0:
                return "Error: 'credit_limit' must be a non-negative integer for CREDIT cards"
            init_balance = 0.0
            init_limit = credit_limit

        # For PREPAID cards, require balance
        elif card_type == "PREPAID":
            if balance is None or balance < 0:
                return "Error: 'balance' must be a non-negative integer for PREPAID cards"
            init_balance = float(balance)
            init_limit = 0.0

        # For DEBIT cards, ignore both
        else:
            init_balance = 0.0
            init_limit = 0.0

        # Generate new card_id
        existing_ids = [int(cid) for cid in cards.keys() if cid.isdigit()]
        new_id_int = max(existing_ids) + 1 if existing_ids else 1
        new_id = str(new_id_int)

        # Generate card_number: use previous ID’s card_number + 1
        prev_key = str(new_id_int - 1)
        if prev_key in cards:
            prev_card_number = cards[prev_key].get('card_number', '')
            if prev_card_number.isdigit():
                card_number = str(int(prev_card_number) + 1)
            else:
                card_number = new_id  # fallback if previous isn’t numeric
        else:
            card_number = new_id  # first card

        now_iso = datetime.now().isoformat()
        issued_date = datetime.now().date().isoformat()

        card = {
            "card_id": new_id_int,
            "account_id": account_id,
            "type": card_type,
            "card_number": card_number,
            "expiry_date": exp_date,
            "issued_date": issued_date,
            "status": "ACTIVE",
            "balance": init_balance,
            "credit_limit": init_limit,
            "created_at": now_iso,
            "updated_at": now_iso
        }

        cards[new_id] = card

        return json.dumps({
            "message": "Card issued successfully",
            "card": card
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "issue_card",
                "description": "Issue a new card: for CREDIT provide credit_limit, for PREPAID provide initial balance, DEBIT requires neither; card_number is previous ID’s number plus one",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "integer",
                            "description": "ID of the account to which the card is issued"
                        },
                        "card_type": {
                            "type": "string",
                            "description": "Type of card to issue (DEBIT, CREDIT, PREPAID)"
                        },
                        "expiry_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Expiry date of the card (YYYY-MM-DD)"
                        },
                        "credit_limit": {
                            "type": "integer",
                            "description": "Credit limit for CREDIT cards (non-negative integer)"
                        },
                        "balance": {
                            "type": "integer",
                            "description": "Initial balance for PREPAID cards (non-negative integer)"
                        }
                    },
                    "required": ["account_id", "card_type", "expiry_date"]
                }
            }
        }
