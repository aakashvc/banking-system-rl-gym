import json
from typing import Any, Dict, Optional
from src.classes.function import Function
from datetime import datetime


class GetAccountSummary(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        account_id: int,
        recent_txns_count: Optional[int] = 3
    ) -> str:
        # account_id is required and must be int or int-like string
        try:
            acct_id = int(account_id)
        except (ValueError, TypeError):
            return "Error: 'account_id' must be an integer"

        # ensure recent_txns_count is an integer
        try:
            count = int(recent_txns_count)
        except (ValueError, TypeError):
            return "Error: 'recent_txns_count' must be an integer"

        accounts = data.get('accounts', {})
        transactions = data.get('transactions', {})

        # Fetch the account
        account = None
        for aid, acc in accounts.items():
            try:
                if int(aid) == acct_id:
                    account = acc
                    break
            except (ValueError, TypeError):
                continue

        if not account:
            return f"Error: Account '{acct_id}' not found"

        balance = account.get('balance')
        status = account.get('status')

        # Collect and sort transactions for this account
        filtered_txns = [
            txn for txn in transactions.values()
            if txn.get('account_id') == acct_id
        ]

        # Parse occurred_at and sort descending
        def parse_date(t: Dict[str, Any]) -> datetime:
            occurred = t.get('occurred_at')
            if isinstance(occurred, str):
                try:
                    return datetime.fromisoformat(occurred)
                except ValueError:
                    pass
            if isinstance(occurred, datetime):
                return occurred
            return datetime.min

        filtered_txns.sort(key=parse_date, reverse=True)
        recent_txns = filtered_txns[:count]

        summary = {
            "balance": balance,
            "status": status,
            "recent_txns": recent_txns
        }
        return json.dumps(summary, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_account_summary",
                "description": "Get balance, status, and recent transactions for an account",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "integer",
                            "description": "Account ID to summarize (required)"
                        },
                        "recent_txns_count": {
                            "type": "integer",
                            "description": "Number of recent transactions to include (default 3)"
                        }
                    },
                    "required": ["account_id"]
                }
            }
        }
