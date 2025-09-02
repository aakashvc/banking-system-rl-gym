import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListBranches(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        branch_id: Optional[int] = None,
        bank_id: Optional[int] = None,
        name: Optional[str] = None,
        address: Optional[str] = None,
        swift_code: Optional[str] = None,
        contact_number: Optional[str] = None
    ) -> str:
        branches = data.get('branches', {})
        results = []

        name_lower = name.lower() if name else None
        address_lower = address.lower() if address else None
        swift_lower = swift_code.lower() if swift_code else None

        for bid, branch in branches.items():
            # Filter by branch_id (exact)
            if branch_id is not None:
                try:
                    if int(bid) != branch_id:
                        continue
                except (ValueError, TypeError):
                    continue

            # Filter by bank_id (exact)
            if bank_id is not None and branch.get('bank_id') != bank_id:
                continue

            # Partial, case-insensitive match on name
            if name_lower and name_lower not in branch.get('name', '').lower():
                continue

            # Partial, case-insensitive match on address
            if address_lower and address_lower not in branch.get('address', '').lower():
                continue

            # Exact, case-insensitive match on SWIFT code
            if swift_lower and branch.get('swift_code', '').lower() != swift_lower:
                continue

            # Exact match on contact number
            if contact_number and branch.get('contact_number') != contact_number:
                continue

            results.append(branch)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_branches",
                "description": "List or filter branches by any field",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_id": {
                            "type": "integer",
                            "description": "Branch ID to filter by (exact match)"
                        },
                        "bank_id": {
                            "type": "integer",
                            "description": "Bank ID to filter by (exact match)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Partial or full branch name (case-insensitive substring match)"
                        },
                        "address": {
                            "type": "string",
                            "description": "Partial or full address (case-insensitive substring match)"
                        },
                        "swift_code": {
                            "type": "string",
                            "description": "SWIFT code (exact match, case-insensitive)"
                        },
                        "contact_number": {
                            "type": "string",
                            "description": "Contact number (exact match)"
                        }
                    },
                    "required": []
                }
            }
        }
