filter_schema = {
    "banks": {
        "*": {
            "bank_id": True,
            "name": True,
            "main_branch_id": True
        }
    },
    "branches": {
        "*": {
            "branch_id": True,
            "bank_id": True,
            "name": True,
            "address": True,
            "swift_code": True,
            "contact_number": True
        }
    },
    "employees": {
        "*": {
            "employee_id": True,
            "branch_id": True,
            "first_name": True,
            "last_name": True,
            "role": True,
            "email": True,
            "phone": True,
            "hire_date": True,
            "status": True,
            "created_at": False,
            "updated_at": False,
        }
    },
    "customers": {
        "*": {
            "customer_id": True,
            "first_name": True,
            "last_name": True,
            "dob": True,
            "email": True,
            "phone": True,
            "address": True,
            "created_at": False,
            "updated_at": False,
        }
    },
    "accounts": {
        "*": {
            "account_id": True,
            "branch_id": True,
            "customer_id": True,
            "account_number": True,
            "type": True,
            "balance": True,
            "opened_date": True,
            "status": True,
            "created_at": False,
            "updated_at": False,
        }
    },
    "transactions": {
        "*": {
            "transaction_id": True,
            "account_id": True,
            "type": True,
            "channel": True,
            "amount": True,
            "occurred_at": True,
            "beneficiary_id": True,
            "card_id": True,
            "merchant": True,
            "card_tx_status": True,
            "created_at": False,
        }
    },
    "beneficiaries": {
        "*": {
            "beneficiary_id": True,
            "customer_id": True,
            "name": True,
            "swift_code": True,
            "beneficiary_type": True,
            "account_number": True,
            "added_at": False,
        }
    },
    "loans": {
        "*": {
            "loan_id": True,
            "customer_id": True,
            "branch_id": True,
            "loan_account_number": True,
            "type": True,
            "principal_amount": True,
            "interest_rate": True,
            "tenure": True,
            "start_date": True,
            "end_date": True,
            "status": True,
            "created_at": False,
        }
    },
    "loan_statements": {
        "*": {
            "statement_id": True,
            "loan_id": True,
            "period_start": True,
            "period_end": True,
            "due_date": True,
            "scheduled_amount": True,
            "late_fee_amount": True,
            "penalty_rate_id": True,
            "status": True,
            "created_at": False,
        }
    },
    "cards": {
        "*": {
            "card_id": True,
            "customer_id": True,
            "type": True,
            "card_number": True,
            "expiry_date": True,
            "issued_date": True,
            "status": True,
            "balance": True,
            "credit_limit": True,
            "created_at": False,
            "updated_at": False,
        }
    },
    "card_statements": {
        "*": {
            "statement_id": True,
            "card_id": True,
            "period_start": True,
            "period_end": True,
            "total_due": True,
            "minimum_due": True,
            "payment_due_date": True,
            "late_fee_amount": True,
            "penalty_rate_id": True,
            "status": True,
            "created_at": False,
        }
    },
    "penalty_rates": {
        "*": {
            "penalty_rate_id": True,
            "product_type": True,
            "product_subtype": True,
            "days_overdue_from": True,
            "days_overdue_to": True,
            "rate": True,
            "created_at": False,
        }
    },
}

