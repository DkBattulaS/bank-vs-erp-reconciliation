import pandas as pd

# Load data
bank_df = pd.read_excel("bank_statement.xlsx")
erp_df = pd.read_excel("erp_ledger.xlsx")

# Function to clean and standardize
def clean_data(df):
    df = df.copy()
    
    # Ensure column names are consistent
    df.columns = df.columns.str.strip().str.lower()
    
    # Standardize columns
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['description'] = df['description'].astype(str).str.lower().str.strip()
    
    # Drop rows with missing critical values
    df = df.dropna(subset=['date', 'amount', 'description'])
    
    return df

# Clean both
bank_df = clean_data(bank_df)
erp_df = clean_data(erp_df)

# Preview
print("✅ Cleaned Bank Data:\n", bank_df.head(3))
print("\n✅ Cleaned ERP Data:\n", erp_df.head(3))
# STEP 6: Exact Matching
matched = pd.merge(bank_df, erp_df, on=['date', 'amount', 'description'], how='inner')

# Entries in bank not in matched
bank_df['key'] = bank_df.apply(lambda row: (row['date'], row['amount'], row['description']), axis=1)
matched['key'] = matched.apply(lambda row: (row['date'], row['amount'], row['description']), axis=1)
unmatched_bank = bank_df[~bank_df['key'].isin(matched['key'])].drop(columns='key')

# Entries in ERP not in matched
erp_df['key'] = erp_df.apply(lambda row: (row['date'], row['amount'], row['description']), axis=1)
unmatched_erp = erp_df[~erp_df['key'].isin(matched['key'])].drop(columns='key')

print(f"\n✅ Matched Entries: {len(matched)}")
print(f"❌ Missing in ERP (only in Bank): {len(unmatched_bank)}")
print(f"❌ Missing in Bank (only in ERP): {len(unmatched_erp)}")


with pd.ExcelWriter("Reconciliation_Report.xlsx", engine='openpyxl') as writer:
    matched.to_excel(writer, sheet_name='Matched Entries', index=False)
    unmatched_bank.to_excel(writer, sheet_name='Only in Bank', index=False)
    unmatched_erp.to_excel(writer, sheet_name='Only in ERP', index=False)

print("\n📁 Report saved as 'Reconciliation_Report.xlsx'")


# Export all reconciliation results for Power BI
matched['Status'] = 'Matched'
unmatched_bank['Status'] = 'Only in Bank'
unmatched_erp['Status'] = 'Only in ERP'

# Combine everything into one table
combined_df = pd.concat([matched, unmatched_bank, unmatched_erp], ignore_index=True)

# Save as CSV
combined_df.to_csv("reconciliation_data.csv", index=False)
print("📁 Reconciliation data exported to 'reconciliation_data.csv' for Power BI.")

