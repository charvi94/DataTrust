import pandas as pd


def normalize_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def find_duplicates(df):

    data = df.copy()

    # Normalize name
    if "name" in data.columns:
        data["normalized_name"] = (
            data["name"].apply(normalize_text)
        )

    # Normalize email
    if "email" in data.columns:
        data["normalized_email"] = (
            data["email"].apply(normalize_text)
        )

    # Find duplicates using name + email
    duplicate_mask = data.duplicated(
        subset=["normalized_name", "normalized_email"],
        keep=False
    )

    duplicates = data[duplicate_mask]

    return duplicates