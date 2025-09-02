import json
from typing import Any, Dict
from src.classes.function import Function
from datetime import datetime


class GetBankByName(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        name: str
    ) -> str:
        banks = data.get('banks', {})
        name_lower = name.lower()

        # Partial, case-insensitive match on bank name
        for bank in banks.values():
            bank_name = bank.get('name', '')
            if name_lower in bank_name.lower():
                return json.dumps(bank)

        return f"Error: Bank matching '{name}' not found"

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_bank_by_name",
                "description": "Fetch a bank record by a partial, case-insensitive name match",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Partial or full name of the bank (case-insensitive)"
                        }
                    },
                    "required": ["name"]
                }
            }
        }
