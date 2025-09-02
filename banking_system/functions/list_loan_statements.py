import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListLoanStatements(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        loan_id: Optional[int] = None,
        period_start_from: Optional[str] = None,
        period_end_to: Optional[str] = None,
        status: Optional[str] = None,
        scheduled_min: Optional[int] = None,
        scheduled_max: Optional[int] = None
    ) -> str:
        statements = data.get('loan_statements', {})
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
            # Filter by loan_id (exact)
            if loan_id is not None and stmt.get('loan_id') != loan_id:
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

            # Filter by scheduled amount range
            sched_amt = stmt.get('scheduled_amount', 0)
            if scheduled_min is not None and sched_amt < scheduled_min:
                continue
            if scheduled_max is not None and sched_amt > scheduled_max:
                continue

            results.append(stmt)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_loan_statements",
                "description": "List or filter loan statements by loan ID, period range, status, and scheduled amount range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "loan_id": {
                            "type": "integer",
                            "description": "Loan ID to filter by (exact match)"
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
                            "description": "Statement status (exact match: PENDING, PAID, OVERDUE)"
                        },
                        "scheduled_min": {
                            "type": "integer",
                            "description": "Minimum scheduled amount (inclusive)"
                        },
                        "scheduled_max": {
                            "type": "integer",
                            "description": "Maximum scheduled amount (inclusive)"
                        }
                    },
                    "required": []
                }
            }
        }
