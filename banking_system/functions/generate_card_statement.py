import json
from typing import Any, Dict
from src.classes.function import Function
from datetime import datetime, timedelta


class GenerateCardStatement(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        card_id: int
    ) -> str:
        cards = data.get('cards', {})
        transactions = data.get('transactions', {})
        statements = data.get('card_statements', {})

        # Validate card_id
        if not isinstance(card_id, int):
            return "Error: 'card_id' must be an integer"
        card = None
        for cid, c in cards.items():
            try:
                if int(cid) == card_id:
                    card = c
                    break
            except (ValueError, TypeError):
                continue
        if card is None:
            return f"Error: Card '{card_id}' not found"

        # Determine period_start and period_end
        card_statements = [s for s in statements.values() if s.get('card_id') == card_id]
        if card_statements:
            prev_end = max(
                datetime.fromisoformat(s['period_end']).date()
                for s in card_statements
            )
        else:
            # first period starts at issue date
            try:
                prev_end = datetime.fromisoformat(card['issued_date']).date() - timedelta(days=1)
            except Exception:
                return "Error: card.issued_date is invalid"

        period_start = prev_end + timedelta(days=1)
        period_end = period_start + timedelta(days=29)  # 30-day billing cycle
        payment_due_date = period_end + timedelta(days=10)

        # Collect relevant transactions and mark them billed
        total_due = 0.0
        for txn in transactions.values():
            if txn.get('card_id') == card_id:
                # parse occurred_at
                occ = txn.get('occurred_at')
                try:
                    occ_dt = datetime.fromisoformat(occ).date() if isinstance(occ, str) else occ.date()
                except Exception:
                    continue
                if period_start <= occ_dt <= period_end:
                    total_due += txn.get('amount', 0)
                    # mark as billed
                    txn['card_tx_status'] = 'BILLED'

        total_due = round(total_due, 2)
        minimum_due = round(total_due * 0.10, 2)  # e.g., 10% minimum payment

        # Generate new statement_id
        existing_ids = [int(sid) for sid in statements.keys() if sid.isdigit()]
        new_sid = str(max(existing_ids) + 1) if existing_ids else "1"
        now_str = datetime.now().isoformat()

        stmt = {
            "statement_id": int(new_sid),
            "card_id": card_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "total_due": total_due,
            "minimum_due": minimum_due,
            "payment_due_date": payment_due_date.isoformat(),
            "late_fee_amount": 0.00,
            "penalty_rate_id": None,
            "status": "OPEN",
            "created_at": now_str
        }

        statements[new_sid] = stmt

        return json.dumps({
            "message": "Card statement generated successfully",
            "statement": stmt
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "generate_card_statement",
                "description": "Create the next billing statement for a card (30-day cycle, due 10 days after period end; marks encompassed transactions as billed)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "card_id": {
                            "type": "integer",
                            "description": "ID of the card for which to generate the statement"
                        }
                    },
                    "required": ["card_id"]
                }
            }
        }
