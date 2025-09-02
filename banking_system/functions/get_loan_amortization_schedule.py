import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime, timedelta


class GetLoanAmortizationSchedule(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        loan_id: int
    ) -> str:
        loans = data.get('loans', {})
        # Find the loan record
        loan: Optional[Dict[str, Any]] = None
        for lid, ln in loans.items():
            try:
                if int(lid) == loan_id:
                    loan = ln
                    break
            except (ValueError, TypeError):
                continue

        if not loan:
            return f"Error: Loan '{loan_id}' not found"

        # Extract loan parameters
        principal = loan.get('principal_amount', 0)
        annual_rate = loan.get('interest_rate', 0)
        tenure = loan.get('tenure', 0)
        start_date_str = loan.get('start_date')

        # Parse start date
        try:
            period_start = datetime.fromisoformat(start_date_str)
        except Exception:
            return f"Error: Invalid start_date '{start_date_str}' for loan '{loan_id}'"

        # Monthly interest rate
        monthly_rate = annual_rate / 100 / 12
        n = tenure if tenure > 0 else 1

        # Calculate fixed monthly payment
        if monthly_rate > 0:
            payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** (-n))
        else:
            payment = principal / n

        # Build the amortization schedule
        schedule = []
        balance = principal

        for _ in range(n):
            interest = balance * monthly_rate
            principal_paid = payment - interest
            # Avoid negative balance in last period
            if principal_paid > balance:
                principal_paid = balance
                payment = principal_paid + interest
            balance -= principal_paid

            # Compute period_end as last day before next month
            year = period_start.year + (period_start.month // 12)
            month = period_start.month % 12 + 1
            first_next_month = period_start.replace(year=year, month=month, day=1)
            period_end = first_next_month - timedelta(days=1)

            schedule.append({
                "period_start": period_start.strftime("%Y-%m-%d"),
                "period_end": period_end.strftime("%Y-%m-%d"),
                "scheduled_amount": round(payment, 2),
                "principal": round(principal_paid, 2),
                "interest": round(interest, 2),
                "balance": round(balance, 2)
            })

            # Advance to next period
            period_start = first_next_month

        return json.dumps(schedule)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_loan_amortization_schedule",
                "description": "Get full amortization breakdown (principal/interest per period)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "loan_id": {
                            "type": "integer",
                            "description": "Loan ID to generate the amortization schedule for"
                        }
                    },
                    "required": ["loan_id"]
                }
            }
        }
