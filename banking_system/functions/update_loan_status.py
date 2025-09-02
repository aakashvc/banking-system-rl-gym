import json
from typing import Any, Dict
from src.classes.function import Function
from datetime import datetime


class UpdateLoanStatus(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        loan_id: int,
        status: str
    ) -> str:
        loans = data.get('loans', {})

        # Validate loan_id
        if not isinstance(loan_id, int):
            return "Error: 'loan_id' must be an integer"

        # Locate loan
        loan_key = None
        for lid in loans:
            try:
                if int(lid) == loan_id:
                    loan_key = lid
                    break
            except (ValueError, TypeError):
                continue
        if loan_key is None:
            return f"Error: Loan '{loan_id}' not found"

        # Validate status
        if not isinstance(status, str):
            return "Error: 'status' must be a string"
        valid_statuses = {"ACTIVE", "CLOSED", "DEFAULTED"}
        if status not in valid_statuses:
            return f"Error: 'status' must be one of: {', '.join(valid_statuses)}"

        # Update loan status
        loan = loans[loan_key]
        loan['status'] = status

        # Optionally set end_date when closing
        if status == "CLOSED":
            loan['end_date'] = datetime.now().date().isoformat()

        return json.dumps(loan, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_loan_status",
                "description": "Change a loan’s status (e.g., to CLOSED or DEFAULTED)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "loan_id": {
                            "type": "integer",
                            "description": "ID of the loan to update"
                        },
                        "status": {
                            "type": "string",
                            "description": "New loan status (ACTIVE, CLOSED, DEFAULTED)"
                        }
                    },
                    "required": ["loan_id", "status"]
                }
            }
        }
