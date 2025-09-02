import json
from typing import Any, Dict
from src.classes.function import Function
from datetime import datetime


class MakePayment(Function):
    @staticmethod
    def apply(
        data: Dict[str, Any],
        account_id: int,
        beneficiary_id: int,
        product_type: str,
        amount: float,
        channel: str
    ) -> str:
        accounts = data.get('accounts', {})
        beneficiaries = data.get('beneficiaries', {})
        loans = data.get('loans', {})
        cards = data.get('cards', {})
        transactions = data.get('transactions', {})
        loan_statements = data.get('loan_statements', {})
        card_statements = data.get('card_statements', {})

        # Validate product_type
        if not isinstance(product_type, str):
            return "Error: 'product_type' must be a string"
        pt = product_type.upper()
        if pt not in {"LOAN", "CARD"}:
            return "Error: 'product_type' must be 'LOAN' or 'CARD'"

        # Validate account_id and locate account
        if not isinstance(account_id, int):
            return "Error: 'account_id' must be an integer"
        acct_key = str(account_id)
        account = accounts.get(acct_key)
        if not account:
            return f"Error: Account '{account_id}' not found"

        # Validate beneficiary_id and locate beneficiary
        ben = beneficiaries.get(str(beneficiary_id))
        if not ben:
            return f"Error: Beneficiary '{beneficiary_id}' not found"

        # Validate amount (float)
        try:
            amount_val = float(amount)
        except (TypeError, ValueError):
            return "Error: 'amount' must be a number"
        if amount_val <= 0:
            return "Error: 'amount' must be greater than 0"

        # Validate channel
        if not isinstance(channel, str):
            return "Error: 'channel' must be a string"

        # Check sufficient funds in source account
        current_balance = float(account.get('balance', 0))
        if amount_val > current_balance:
            return "Error: Insufficient funds"

        # Deduct from source account
        now_iso = datetime.now().isoformat()
        account['balance'] = round(current_balance - amount_val, 2)
        account['updated_at'] = now_iso

        card_id = None  # will set if CARD

        # Helper: parse datetime from transactions
        def _parse_dt(val: Any) -> datetime:
            if isinstance(val, datetime):
                return val
            if isinstance(val, str):
                try:
                    return datetime.fromisoformat(val)
                except ValueError:
                    return datetime.min
            return datetime.min

        # ---------- LOAN payments ----------
        if pt == "LOAN":
            if ben.get('beneficiary_type') != 'LOAN_ACCOUNT':
                return "Error: Beneficiary is not a loan account"

            loan_acct_num = ben.get('account_number')
            # find loan by loan_account_number
            loan_obj = next((ln for ln in loans.values()
                             if ln.get('loan_account_number') == loan_acct_num), None)
            if not loan_obj:
                return f"Error: No loan found for beneficiary account '{loan_acct_num}'"

            # Find latest statement (by period_end) for this loan
            latest_stmt_key = None
            latest_period_end = None
            latest_period_start = None
            for sid, stmt in loan_statements.items():
                if stmt.get('loan_id') == loan_obj.get('loan_id'):
                    try:
                        pe = datetime.fromisoformat(stmt.get('period_end')).date() if isinstance(stmt.get('period_end'), str) else stmt.get('period_end')
                        ps = datetime.fromisoformat(stmt.get('period_start')).date() if isinstance(stmt.get('period_start'), str) else stmt.get('period_start')
                    except Exception:
                        pe, ps = None, None
                    if pe and (latest_period_end is None or pe > latest_period_end):
                        latest_period_end = pe
                        latest_period_start = ps
                        latest_stmt_key = sid

            # If there is a latest statement and it's not PAID, sum payments from that period_start onward
            if latest_stmt_key is not None:
                stmt = loan_statements[latest_stmt_key]
                if stmt.get('status') != 'PAID' and latest_period_start is not None:
                    start_dt = datetime.combine(latest_period_start, datetime.min.time())
                    total_paid = 0.0
                    for tx in transactions.values():
                        if tx.get('type') == 'PAYMENT' and tx.get('beneficiary_id') == beneficiary_id:
                            occ = _parse_dt(tx.get('occurred_at'))
                            if occ >= start_dt:
                                try:
                                    total_paid += float(tx.get('amount', 0))
                                except (TypeError, ValueError):
                                    continue
                    total_paid += amount_val  # include this payment
                    scheduled = float(stmt.get('scheduled_amount', 0))
                    if total_paid >= scheduled:
                        stmt['status'] = 'PAID'

        # ---------- CARD payments ----------
        else:
            if ben.get('beneficiary_type') != 'CARD':
                return "Error: Beneficiary is not a card"
            card_num = ben.get('account_number')

            # locate card by card_number
            found_key = None
            card = None
            for k, c in cards.items():
                if c.get('card_number') == card_num:
                    found_key = k
                    card = c
                    break
            if found_key is None or not card:
                return f"Error: No card found for beneficiary account '{card_num}'"

            ctype = card.get('type')
            if ctype == 'CREDIT':
                # Credit payment increases available limit (reduces outstanding)
                new_limit = float(card.get('credit_limit', 0)) + amount_val
                card['credit_limit'] = round(new_limit, 2)
                card['updated_at'] = now_iso

                # Find latest statement (by period_end) for this card
                latest_stmt_key = None
                latest_period_end = None
                latest_period_start = None
                for sid, stmt in card_statements.items():
                    if stmt.get('card_id') == card.get('card_id'):
                        try:
                            pe = datetime.fromisoformat(stmt.get('period_end')).date() if isinstance(stmt.get('period_end'), str) else stmt.get('period_end')
                            ps = datetime.fromisoformat(stmt.get('period_start')).date() if isinstance(stmt.get('period_start'), str) else stmt.get('period_start')
                        except Exception:
                            pe, ps = None, None
                        if pe and (latest_period_end is None or pe > latest_period_end):
                            latest_period_end = pe
                            latest_period_start = ps
                            latest_stmt_key = sid

                # If there is a latest statement and it's not PAID, sum payments from that period_start onward
                if latest_stmt_key is not None:
                    stmt = card_statements[latest_stmt_key]
                    if stmt.get('status') != 'PAID' and latest_period_start is not None:
                        start_dt = datetime.combine(latest_period_start, datetime.min.time())
                        total_paid = 0.0
                        for tx in transactions.values():
                            if tx.get('type') == 'PAYMENT' and tx.get('beneficiary_id') == beneficiary_id:
                                occ = _parse_dt(tx.get('occurred_at'))
                                if occ >= start_dt:
                                    try:
                                        total_paid += float(tx.get('amount', 0))
                                    except (TypeError, ValueError):
                                        continue
                        total_paid += amount_val  # include this payment
                        total_due = float(stmt.get('total_due', 0))
                        if total_paid >= total_due:
                            stmt['status'] = 'PAID'

            elif ctype == 'PREPAID':
                # Prepaid payment increases stored balance
                new_bal = float(card.get('balance', 0)) + amount_val
                card['balance'] = round(new_bal, 2)
                card['updated_at'] = now_iso
                # No statements logic for prepaid
            else:
                return f"Error: Cannot make payment to a {ctype} card"

            card_id = int(found_key)

        # Generate new transaction_id
        existing_ids = [int(tid) for tid in transactions.keys() if tid.isdigit()]
        new_txn_id = str(max(existing_ids) + 1) if existing_ids else "1"

        txn = {
            "transaction_id": int(new_txn_id),
            "account_id": account_id,
            "type": "PAYMENT",
            "channel": channel,
            "amount": round(amount_val, 2),
            "occurred_at": now_iso,
            "beneficiary_id": beneficiary_id,
            "card_id": card_id,
            "merchant": None,
            "card_tx_status": None,
            "created_at": now_iso
        }
        transactions[new_txn_id] = txn

        message = "Loan payment successful" if pt == "LOAN" else "Card payment successful"
        return json.dumps({
            "message": message,
            "transaction": txn
        }, default=str)

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "make_payment",
                "description": "Record a payment to a saved LOAN or CARD beneficiary. For the latest statement, sum payments from that statement's period_start (inclusive) and auto-close when paid.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "integer",
                            "description": "ID of the account from which to pay"
                        },
                        "beneficiary_id": {
                            "type": "integer",
                            "description": "ID of the saved beneficiary"
                        },
                        "product_type": {
                            "type": "string",
                            "description": "Product type: 'LOAN' or 'CARD'"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Payment amount (number; decimals allowed)"
                        },
                        "channel": {
                            "type": "string",
                            "description": "Payment channel (BRANCH, ONLINE, MOBILE, ATM)"
                        }
                    },
                    "required": ["account_id", "beneficiary_id", "product_type", "amount", "channel"]
                }
            }
        }
