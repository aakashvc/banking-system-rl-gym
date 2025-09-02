import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListCustomerLoans(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        loan_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        branch_id: Optional[int] = None,
        loan_type: Optional[str] = None,
        status: Optional[str] = None,
        principal_min: Optional[int] = None,
        principal_max: Optional[int] = None,
        interest_min: Optional[int] = None,
        interest_max: Optional[int] = None
    ) -> str:
        loans = data.get('loans', {})
        results = []

        for lid, ln in loans.items():
            # Filter by loan_id (exact)
            if loan_id is not None:
                try:
                    if int(lid) != loan_id:
                        continue
                except (ValueError, TypeError):
                    continue

            # Filter by customer_id (exact)
            if customer_id is not None and ln.get('customer_id') != customer_id:
                continue

            # Filter by branch_id (exact)
            if branch_id is not None and ln.get('branch_id') != branch_id:
                continue

            # Filter by loan_type (exact, case-insensitive)
            if loan_type and ln.get('type', '').lower() != loan_type.lower():
                continue

            # Filter by status (exact, case-insensitive)
            if status and ln.get('status', '').lower() != status.lower():
                continue

            # Filter by principal range
            principal = ln.get('principal_amount', 0)
            if principal_min is not None and principal < principal_min:
                continue
            if principal_max is not None and principal > principal_max:
                continue

            # Filter by interest rate range
            interest = ln.get('interest_rate', 0)
            if interest_min is not None and interest < interest_min:
                continue
            if interest_max is not None and interest > interest_max:
                continue

            results.append(ln)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_customer_loans",
                "description": "List or filter loans for a customer by various fields",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "loan_id": {
                            "type": "integer",
                            "description": "Loan ID to filter by (exact match)"
                        },
                        "customer_id": {
                            "type": "integer",
                            "description": "Customer ID to filter by (exact match)"
                        },
                        "branch_id": {
                            "type": "integer",
                            "description": "Branch ID to filter by (exact match)"
                        },
                        "loan_type": {
                            "type": "string",
                            "description": "Loan type (HOME, CAR, PERSONAL, EDUCATION)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Loan status (ACTIVE, CLOSED, DEFAULTED)"
                        },
                        "principal_min": {
                            "type": "integer",
                            "description": "Minimum principal amount (inclusive)"
                        },
                        "principal_max": {
                            "type": "integer",
                            "description": "Maximum principal amount (inclusive)"
                        },
                        "interest_min": {
                            "type": "integer",
                            "description": "Minimum interest rate (inclusive, in basis points or percent units)"
                        },
                        "interest_max": {
                            "type": "integer",
                            "description": "Maximum interest rate (inclusive, in basis points or percent units)"
                        }
                    },
                    "required": []
                }
            }
        }
