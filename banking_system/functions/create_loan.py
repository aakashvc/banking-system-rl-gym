import json
from typing import Any, Dict
from src.classes.function import Function
from datetime import datetime


class CreateLoan(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        customer_id: int,
        branch_id: int,
        loan_type: str,
        principal_amount: int,
        interest_rate: float,
        tenure_months: int,
        start_date: str
    ) -> str:
        customers = data.get('customers', {})
        branches = data.get('branches', {})
        loans = data.get('loans', {})

        # Validate customer_id
        if not isinstance(customer_id, int):
            return "Error: 'customer_id' must be an integer"
        if str(customer_id) not in customers:
            return f"Error: Customer '{customer_id}' not found"

        # Validate branch_id
        if not isinstance(branch_id, int):
            return "Error: 'branch_id' must be an integer"
        if str(branch_id) not in branches:
            return f"Error: Branch '{branch_id}' not found"

        # Validate loan_type
        if not isinstance(loan_type, str):
            return "Error: 'loan_type' must be a string"

        # Validate principal_amount
        if not isinstance(principal_amount, int) or principal_amount <= 0:
            return "Error: 'principal_amount' must be a positive integer"

        # Validate interest_rate (allow float)
        try:
            ir = float(interest_rate)
        except (TypeError, ValueError):
            return "Error: 'interest_rate' must be a number"
        if ir < 0:
            return "Error: 'interest_rate' must be non-negative"

        # Validate tenure_months
        if not isinstance(tenure_months, int) or tenure_months <= 0:
            return "Error: 'tenure_months' must be a positive integer"

        # Validate start_date
        try:
            parsed_start = datetime.fromisoformat(start_date).date()
            start_date_str = parsed_start.isoformat()
        except Exception:
            return "Error: 'start_date' must be a string in YYYY-MM-DD format"

        # Generate new loan_id
        existing_ids = [int(lid) for lid in loans.keys() if lid.isdigit()]
        new_id_int = max(existing_ids) + 1 if existing_ids else 1
        new_id = str(new_id_int)

        # Determine loan_account_number: one more than the previous loan's number
        prev_key = str(new_id_int - 1)
        if prev_key in loans:
            prev_num_str = loans[prev_key].get('loan_account_number', '')
            try:
                prev_num_int = int(prev_num_str)
                loan_account_number = str(prev_num_int + 1)
            except (ValueError, TypeError):
                loan_account_number = new_id  # fallback if previous number isn't numeric
        else:
            loan_account_number = new_id

        now_str = datetime.now().isoformat()

        loan = {
            "loan_id": new_id_int,
            "customer_id": customer_id,
            "branch_id": branch_id,
            "loan_account_number": loan_account_number,
            "type": loan_type,
            "principal_amount": principal_amount,
            "interest_rate": ir,
            "tenure": tenure_months,
            "start_date": start_date_str,
            "end_date": None,
            "status": "ACTIVE",
            "created_at": now_str
        }

        loans[new_id] = loan

        return json.dumps({
            "message": "Loan created successfully",
            "loan": loan
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_loan",
                "description": "Create a new loan account; loan_account_number is one more than the previous loan's number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "ID of the customer taking the loan"
                        },
                        "branch_id": {
                            "type": "integer",
                            "description": "ID of the branch issuing the loan"
                        },
                        "loan_type": {
                            "type": "string",
                            "description": "Type of loan (HOME, CAR, PERSONAL, EDUCATION)"
                        },
                        "principal_amount": {
                            "type": "integer",
                            "description": "Principal loan amount (integer)"
                        },
                        "interest_rate": {
                            "type": "number",
                            "description": "Interest rate as a number (decimals allowed, e.g., 7.25)"
                        },
                        "tenure_months": {
                            "type": "integer",
                            "description": "Loan tenure in months"
                        },
                        "start_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Loan start date (YYYY-MM-DD)"
                        }
                    },
                    "required": [
                        "customer_id",
                        "branch_id",
                        "loan_type",
                        "principal_amount",
                        "interest_rate",
                        "tenure_months",
                        "start_date"
                    ]
                }
            }
        }
