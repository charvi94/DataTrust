from services.validator import load_data
from services.cleaner import clean_dataframe


file_path = "uploads/customers.csv"

df = load_data(file_path)

print("\n===== ORIGINAL DATA =====")
print(df)

cleaned_df = clean_dataframe(df)

print("\n===== CLEANED DATA =====")
print(cleaned_df)