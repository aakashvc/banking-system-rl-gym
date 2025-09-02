import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class ListPenaltyRates(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        product_type: Optional[str] = None,
        product_subtype: Optional[str] = None,
        overdue_days: Optional[int] = None
    ) -> str:
        penalty_rates = data.get('penalty_rates', {})
        results = []

        for pr_id, rate in penalty_rates.items():
            # Filter by product_type (exact)
            if product_type and rate.get('product_type') != product_type:
                continue

            # Filter by product_subtype (exact)
            if product_subtype and rate.get('product_subtype') != product_subtype:
                continue

            # If overdue_days provided, it must fall within the rate's range
            if overdue_days is not None:
                from_days = rate.get('days_overdue_from', 0)
                to_days = rate.get('days_overdue_to')
                if overdue_days < from_days:
                    continue
                if to_days is not None and overdue_days > to_days:
                    continue

            results.append(rate)

        return json.dumps(results)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_penalty_rates",
                "description": "List or filter penalty rates by product type, subtype, and optionally a specific overdue days value",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_type": {
                            "type": "string",
                            "description": "Product type (LOAN or CARD)"
                        },
                        "product_subtype": {
                            "type": "string",
                            "description": "Product subtype (HOME, CAR, PERSONAL, EDUCATION, or CREDIT)"
                        },
                        "overdue_days": {
                            "type": "integer",
                            "description": "Number of days overdue; if provided, returns only rates where this value falls between days_overdue_from and days_overdue_to"
                        }
                    },
                    "required": []
                }
            }
        }
