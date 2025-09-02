import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListCardStatements(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        card_id: Optional[int] = None,
        period_start_from: Optional[str] = None,
        period_end_to: Optional[str] = None,
        status: Optional[str] = None,
        total_due_min: Optional[int] = None,
        total_due_max: Optional[int] = None
    ) -> str:
        statements = data.get('card_statements', {})
        results = []

        def parse_date_str(d: Optional[str]) -> Optional[datetime.date]:
            if not d:
                return None
            try:
                return datetime.fromisoformat(d).date()
            except Exception:
                return None

        ps_filter = parse_date_str(period_start_from)
        pe_filter = parse_date_str(period_end_to)

        for sid, stmt in statements.items():
            # Filter by card_id (exact)
            if card_id is not None and stmt.get('card_id') != card_id:
                continue

            # Filter by period_start_from (inclusive)
            ps = parse_date_str(stmt.get('period_start'))
            if ps_filter and (ps is None or ps < ps_filter):
                continue

            # Filter by period_end_to (inclusive)
            pe = parse_date_str(stmt.get('period_end'))
            if pe_filter and (pe is None or pe > pe_filter):
                continue

            # Filter by status (exact, case-insensitive)
            if status and stmt.get('status', '').lower() != status.lower():
                continue

            # Filter by total_due range
            total_due = stmt.get('total_due', 0)
            if total_due_min is not None and total_due < total_due_min:
                continue
            if total_due_max is not None and total_due > total_due_max:
                continue

            results.append(stmt)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_card_statements",
                "description": "List or filter billing statements for a card by various fields",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "card_id": {
                            "type": "integer",
                            "description": "Card ID to filter by (exact match)"
                        },
                        "period_start_from": {
                            "type": "string",
                            "description": "Earliest period_start date as YYYY-MM-DD (inclusive)"
                        },
                        "period_end_to": {
                            "type": "string",
                            "description": "Latest period_end date as YYYY-MM-DD (inclusive)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Statement status (exact match: OPEN, CLOSED, PAID, OVERDUE)"
                        },
                        "total_due_min": {
                            "type": "integer",
                            "description": "Minimum total due amount (inclusive)"
                        },
                        "total_due_max": {
                            "type": "integer",
                            "description": "Maximum total due amount (inclusive)"
                        }
                    },
                    "required": []
                }
            }
        }
