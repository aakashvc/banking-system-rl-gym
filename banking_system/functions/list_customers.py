import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListCustomers(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        customer_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        customers = data.get('customers', {})
        results = []

        # prepare lowercase filters for partial match on names
        first_lower = first_name.lower() if first_name else None
        last_lower = last_name.lower() if last_name else None
        email_lower = email.lower() if email else None

        for cid, cust in customers.items():
            # Filter by customer_id (exact)
            if customer_id is not None:
                try:
                    if int(cid) != customer_id:
                        continue
                except (ValueError, TypeError):
                    continue

            # Partial, case-insensitive match on first_name
            if first_lower and first_lower not in cust.get('first_name', '').lower():
                continue

            # Partial, case-insensitive match on last_name
            if last_lower and last_lower not in cust.get('last_name', '').lower():
                continue

            # Exact, case-insensitive match on email
            if email_lower and cust.get('email', '').lower() != email_lower:
                continue

            # Exact match on phone
            if phone and cust.get('phone') != phone:
                continue

            # Exact match on status
            if status and cust.get('status') != status:
                continue

            results.append(cust)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_customers",
                "description": "Search or filter customers by any field",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "integer",
                            "description": "Customer ID to filter by (exact match)"
                        },
                        "first_name": {
                            "type": "string",
                            "description": "Partial or full first name (case-insensitive substring match)"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Partial or full last name (case-insensitive substring match)"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email address (exact match, case-insensitive)"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Phone number (exact match)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Customer status (exact match, e.g., ACTIVE, INACTIVE)"
                        }
                    },
                    "required": []
                }
            }
        }
