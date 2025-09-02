import json
import random
from typing import Any, Dict
from src.classes.function import Function
from datetime import datetime, timedelta, date


class GenerateLoanStatement(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        loan_id: int
    ) -> str:
        loans = data.get('loans', {})
        statements = data.get('loan_statements', {})
        transactions = data.get('transactions', {})
        penalty_rates = data.get('penalty_rates', {})

        # Validate loan_id
        if not isinstance(loan_id, int):
            return "Error: 'loan_id' must be an integer"
        loan = next((ln for lid, ln in loans.items()
                     if str(ln.get('loan_id')) == str(loan_id)), None)
        if loan is None:
            return f"Error: Loan '{loan_id}' not found"

        # Determine period_start and period_end
        # Find latest statement for this loan
        loan_statements = [s for s in statements.values() if s.get('loan_id') == loan_id]
        if loan_statements:
            # latest period_end
            prev_end = max(
                datetime.fromisoformat(s['period_end']).date()
                for s in loan_statements
            )
        else:
            # first period starts at loan start_date
            try:
                prev_end = datetime.fromisoformat(loan.get('start_date')).date() - timedelta(days=1)
            except Exception:
                return "Error: loan.start_date invalid"

        period_start = prev_end + timedelta(days=1)
        period_end = period_start + timedelta(days=29)  # 30-day period
        due_date = period_end + timedelta(days=10)

        # Calculate scheduled amount
        P = loan.get('principal_amount', 0)
        annual_rate = loan.get('interest_rate', 0)
        n = loan.get('tenure', 1)
        r = annual_rate / 100 / 12
        if r > 0:
            sched = P * r * (1 + r)**n / ((1 + r)**n - 1)
        else:
            sched = P / n
        sched = round(sched, 2)

        # Prepare new statement
        existing_ids = [int(sid) for sid in statements.keys() if sid.isdigit()]
        new_sid = str(max(existing_ids) + 1) if existing_ids else "1"
        now = datetime.now().isoformat()

        stmt = {
            "statement_id": int(new_sid),
            "loan_id": loan_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "due_date": due_date.isoformat(),
            "scheduled_amount": sched,
            "late_fee_amount": 0.00,
            "penalty_rate_id": None,
            "status": "PENDING",
            "created_at": now
        }

        # Check for transactions in period before due_date
        paid = any(
            t for t in transactions.values()
            if t.get('loan_id') == loan_id and
               period_start <= datetime.fromisoformat(t.get('occurred_at')).date() <= due_date
        )

        today = datetime.now().date()
        if due_date < today and not paid:
            # calculate days overdue
            days_overdue = (today - due_date).days
            # find penalty rate
            pr = next((pr for pr in penalty_rates.values()
                       if pr.get('product_type') == 'LOAN'
                       and pr.get('product_subtype') == loan.get('type')
                       and days_overdue >= pr.get('days_overdue_from', 0)
                       and (pr.get('days_overdue_to') is None or days_overdue <= pr.get('days_overdue_to'))),
                      None)
            if pr:
                stmt['late_fee_amount'] = round(sched * pr['rate'] / 100, 2)
                stmt['penalty_rate_id'] = pr['penalty_rate_id']

        statements[new_sid] = stmt

        return json.dumps({
            "message": "Loan statement generated",
            "statement": stmt
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "generate_loan_statement",
                "description": "Generate the next loan statement: 30-day period since last statement, due 10 days after, and apply late fees if unpaid",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "loan_id": {
                            "type": "integer",
                            "description": "ID of the loan"
                        }
                    },
                    "required": ["loan_id"]
                }
            }
        }

