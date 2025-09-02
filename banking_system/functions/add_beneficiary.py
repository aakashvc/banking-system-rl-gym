import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class AddBeneficiary(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        customer_id: int,
        name: str,
        beneficiary_type: str,
        account_number: str,
        swift_code: Optional[str] = None
    ) -> str:
        customers = data.get('customers', {})
        beneficiaries = data.get('beneficiaries', {})

        # Validate customer_id
        if not isinstance(customer_id, int):
            return "Error: 'customer_id' must be an integer"
        if str(customer_id) not in customers:
            return f"Error: Customer '{customer_id}' not found"

        # Validate name
        if not isinstance(name, str) or not name:
            return "Error: 'name' must be a non-empty string"

        # Validate beneficiary_type
        if not isinstance(beneficiary_type, str):
            return "Error: 'beneficiary_type' must be a string"

        # If bank account, require SWIFT code
        if beneficiary_type == 'BANK_ACCOUNT':
            if not isinstance(swift_code, str) or not swift_code.strip():
                return "Error: 'swift_code' is required when beneficiary_type is 'BANK_ACCOUNT'"

        # Validate account_number
        if not isinstance(account_number, str) or not account_number:
            return "Error: 'account_number' must be a non-empty string"

        # Validate swift_code type if provided
        if swift_code is not None and not isinstance(swift_code, str):
            return "Error: 'swift_code' must be a string"

        # Generate new beneficiary_id
        existing_ids = [int(bid) for bid in beneficiaries.keys() if bid.isdigit()]
        new_id = str(max(existing_ids) + 1) if existing_ids else "1"

        now_str = datetime.now().isoformat()

        beneficiary = {
            "beneficiary_id": int(new_id),
            "customer_id": customer_id,
            "name": name,
            "swift_code": swift_code,
            "beneficiary_type": beneficiary_type,
            "account_number": account_number,
            "added_at": now_str
        }

        beneficiaries[new_id] = beneficiary

        return json.dumps({
            "message": "Beneficiary added successfully",
            "beneficiary": beneficiary
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_beneficiary",
                "description": "Save a new beneficiary or payee for a customer; SWIFT code required for BANK_ACCOUNT type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "ID of the customer adding the beneficiary"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the beneficiary"
                        },
                        "beneficiary_type": {
                            "type": "string",
                            "description": "Type of beneficiary (LOAN_ACCOUNT, CARD, BANK_ACCOUNT)"
                        },
                        "account_number": {
                            "type": "string",
                            "description": "Account number of the beneficiary"
                        },
                        "swift_code": {
                            "type": "string",
                            "description": "SWIFT code of the beneficiary (required if beneficiary_type is 'BANK_ACCOUNT')"
                        }
                    },
                    "required": ["customer_id", "name", "beneficiary_type", "account_number"]
                }
            }
        }
