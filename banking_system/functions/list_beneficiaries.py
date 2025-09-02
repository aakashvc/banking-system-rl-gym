import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListBeneficiaries(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        customer_id: Optional[int] = None,
        name: Optional[str] = None,
        swift_code: Optional[str] = None,
        beneficiary_type: Optional[str] = None,
        account_number: Optional[str] = None
    ) -> str:
        beneficiaries = data.get('beneficiaries', {})
        results = []

        # prepare lowercase filter for partial match on name
        name_lower = name.lower() if name else None
        swift_lower = swift_code.lower() if swift_code else None

        for bid, ben in beneficiaries.items():
            # Filter by customer_id (exact)
            if customer_id is not None and ben.get('customer_id') != customer_id:
                continue

            # Partial, case-insensitive match on name
            if name_lower and name_lower not in ben.get('name', '').lower():
                continue

            # Exact, case-insensitive match on SWIFT code
            if swift_lower and ben.get('swift_code', '').lower() != swift_lower:
                continue

            # Exact match on beneficiary_type
            if beneficiary_type and ben.get('beneficiary_type') != beneficiary_type:
                continue

            # Exact match on account_number
            if account_number and ben.get('account_number') != account_number:
                continue

            results.append(ben)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_beneficiaries",
                "description": "List or filter all beneficiaries for a customer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "Customer ID to filter by (exact match)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Partial or full beneficiary name (case-insensitive substring match)"
                        },
                        "swift_code": {
                            "type": "string",
                            "description": "SWIFT code (exact match, case-insensitive)"
                        },
                        "beneficiary_type": {
                            "type": "string",
                            "description": "Type of beneficiary (exact match: LOAN_ACCOUNT, CARD, BANK_ACCOUNT)"
                        },
                        "account_number": {
                            "type": "string",
                            "description": "Account number (exact match)"
                        }
                    },
                    "required": []
                }
            }
        }
