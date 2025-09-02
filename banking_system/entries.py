entries = [
  {
    "id": "entry_1",
    "instructions": "Your name is Lucas Leon (lucas.leon3@example.com). You need to transfer $200 from your checking account to your savings account at Davidshire Branch of “Union Bank“ under the beneficiary name “Own Savings Davidshire” if it doesn't already exist. After completing the transfer, you would also like to freeze the checking account and check its summary.",
    "actions": [
      {
        "name": "list_customers",
        "arguments": {
          "first_name": "Lucas",
          "last_name": "Leon",
          "email": "lucas.leon3@example.com"
        }
      },
      {
        "name": "list_customer_accounts",
        "arguments": {
          "customer_id": 3
        }
      },
      {
        "name": "get_account_summary",
        "arguments": {
          "account_id": 4,
          "recent_txns_count": 3
        }
      },
      {
        "name": "get_bank_by_name",
        "arguments": {
          "name": "Union Bank"
        }
      },
      {
        "name": "list_branches",
        "arguments": {
          "bank_id": 7,
          "name": "Davidshire"
        }
      },
      {
        "name": "list_beneficiaries",
        "arguments": {
          "customer_id": 3
        }
      },
      {
        "name": "add_beneficiary",
        "arguments": {
          "customer_id": 3,
          "name": "Own Savings Davidshire",
          "beneficiary_type": "BANK_ACCOUNT",
          "account_number": "079698883989",
          "swift_code": "ET34QF75"
        }
      },
      {
        "name": "transfer_to_other_bank_account",
        "arguments": {
          "from_account_id": 4,
          "beneficiary_id": 924,
          "amount": 200.00
        }
      },
      {
        "name": "update_account",
        "arguments": {
          "account_id": 4,
          "status": "FROZEN"
        }
      },
      {
        "name": "get_account_summary",
        "arguments": {
          "account_id": 4
        }
      }
    ],
    "outputs": [
        "Own Savings Davidshire",
        "Frozen",
        "$92.85"
    ]
  }
]
