import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)

def generate_transactions(n, start_date):
    data = []
    for _ in range(n):
        date = start_date + timedelta(days=random.randint(0, 90))
        amount = round(random.uniform(100, 10000), 2)

        desc_type = random.choice([
            "Invoice Payment",
            "Vendor Payment",
            "Office Rent",
            "Salary Transfer",
            "Travel Expense",
            "Bank Charges",
            "Service Fee",
            "Equipment Purchase",
            "Customer Refund",
            "Insurance Payout"
        ])
        company = fake.company()
        description = f"{desc_type} - {company}"
        data.append([date.strftime('%Y-%m-%d'), amount, description])

    return pd.DataFrame(data, columns=['Date', 'Amount', 'Description'])

# Base date
base_date = datetime(2025, 1, 1)

# Step 1: Generate 1200 bank transactions
bank_df = generate_transactions(1200, base_date)

# Step 2: Sample 900 for ERP (will add noise)
erp_df = bank_df.sample(900, random_state=1).copy()

# Add mismatches in ERP descriptions/dates
for i in erp_df.index:
    if random.random() < 0.5:
        erp_df.at[i, 'Description'] = erp_df.at[i, 'Description'].replace(" -", "").replace("Payment", "Txn").replace("Transfer", "Txn")
    if random.random() < 0.3:
        date_obj = datetime.strptime(erp_df.at[i, 'Date'], '%Y-%m-%d')
        erp_df.at[i, 'Date'] = (date_obj + timedelta(days=random.choice([-1, 1, 2]))).strftime('%Y-%m-%d')

# Step 3: Add 300 new (unmatched) ERP entries
erp_extra = generate_transactions(300, base_date)
erp_df = pd.concat([erp_df, erp_extra], ignore_index=True)

# Optional: Add a few exact duplicates
dup_entries = bank_df.sample(10, random_state=5)
bank_df = pd.concat([bank_df, dup_entries], ignore_index=True)

# Save to Excel
bank_df.to_excel("bank_statement.xlsx", index=False)
erp_df.to_excel("erp_ledger.xlsx", index=False)

print("✅ Generated LARGE bank_statement.xlsx and erp_ledger.xlsx successfully!")
