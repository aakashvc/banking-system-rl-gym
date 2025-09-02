import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class CreateCustomer(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        first_name: str,
        last_name: str,
        dob: str,
        email: str,
        phone: str,
        address: str
    ) -> str:
        customers = data.get('customers', {})

        # Validate and normalize date of birth (string input)
        try:
            parsed_dob = datetime.fromisoformat(dob).date()
            dob_str = parsed_dob.isoformat()
        except Exception:
            return "Error: 'dob' must be a string in YYYY-MM-DD format"

        # Generate new customer ID
        existing_ids = [int(cid) for cid in customers.keys() if cid.isdigit()]
        new_id = str(max(existing_ids) + 1) if existing_ids else "1"

        now_str = datetime.now().isoformat()

        # Create customer record
        customer = {
            "customer_id": int(new_id),
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob_str,
            "email": email,
            "phone": phone,
            "address": address,
            "status": "ACTIVE",
            "created_at": now_str,
            "updated_at": now_str
        }

        customers[new_id] = customer

        return json.dumps({
            "message": "Customer created successfully",
            "customer": customer
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_customer",
                "description": "Add a new customer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "first_name": {
                            "type": "string",
                            "description": "Customer's first name"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Customer's last name"
                        },
                        "dob": {
                            "type": "string",
                            "format": "date",
                            "description": "Date of birth as a string in YYYY-MM-DD format"
                        },
                        "email": {
                            "type": "string",
                            "description": "Unique email address"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Contact phone number"
                        },
                        "address": {
                            "type": "string",
                            "description": "Residential address"
                        }
                    },
                    "required": ["first_name", "last_name", "dob", "email", "phone", "address"]
                }
            }
        }
