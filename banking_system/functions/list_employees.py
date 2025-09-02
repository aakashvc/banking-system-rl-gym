import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListEmployees(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        employee_id: Optional[int] = None,
        branch_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        employees = data.get('employees', {})
        results = []

        # prepare lowercase filters for partial match on names
        first_lower = first_name.lower() if first_name else None
        last_lower = last_name.lower() if last_name else None
        email_lower = email.lower() if email else None

        for eid, emp in employees.items():
            # Filter by employee_id (exact)
            if employee_id is not None:
                try:
                    if int(eid) != employee_id:
                        continue
                except (ValueError, TypeError):
                    continue

            # Filter by branch_id (exact)
            if branch_id is not None and emp.get('branch_id') != branch_id:
                continue

            # Partial, case-insensitive match on first_name
            if first_lower and first_lower not in emp.get('first_name', '').lower():
                continue

            # Partial, case-insensitive match on last_name
            if last_lower and last_lower not in emp.get('last_name', '').lower():
                continue

            # Exact match on role
            if role and emp.get('role') != role:
                continue

            # Exact, case-insensitive match on email
            if email_lower and emp.get('email', '').lower() != email_lower:
                continue

            # Exact match on phone
            if phone and emp.get('phone') != phone:
                continue

            # Exact match on status
            if status and emp.get('status') != status:
                continue

            results.append(emp)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_employees",
                "description": "List or filter employees by any field",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "integer",
                            "description": "Employee ID to filter by (exact match)"
                        },
                        "branch_id": {
                            "type": "integer",
                            "description": "Branch ID to filter by (exact match)"
                        },
                        "first_name": {
                            "type": "string",
                            "description": "Partial or full first name (case-insensitive substring match)"
                        },
                        "last_name": {
                            "type": "string",
                            "description": "Partial or full last name (case-insensitive substring match)"
                        },
                        "role": {
                            "type": "string",
                            "description": "Role (exact match: TELLER, MANAGER, etc.)"
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
                            "description": "Employment status (exact match: ACTIVE, INACTIVE, ON_LEAVE)"
                        }
                    },
                    "required": []
                }
            }
        }
