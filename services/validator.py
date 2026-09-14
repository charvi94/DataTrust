import pandas as pd
import re


# ==========================================
# LOAD DATA
# ==========================================

def load_data(file_path):

    df = pd.read_csv(
        file_path,
        dtype={"phone": "string"}
    )

    return df


# ==========================================
# EMAIL VALIDATION
# ==========================================

def is_valid_email(email):

    if not email:
        return False

    email = str(email).strip()

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(
        re.match(pattern, email)
    )


# ==========================================
# VALIDATE DATASET
# ==========================================

def validate_data(df):

    results = {

        "total_records": len(df),

        "missing_values": 0,

        "invalid_emails": 0,

        "invalid_phones": 0,

        "invalid_names": 0,

        "invalid_cities": 0
    }


    # ======================================
    # MISSING VALUES
    # ======================================

    results["missing_values"] = int(
        df.isnull().sum().sum()
    )


    # ======================================
    # EMAIL VALIDATION
    # ======================================

    if "email" in df.columns:

        emails = (
            df["email"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        invalid_emails = ~emails.apply(
            is_valid_email
        )

        # Do not count empty emails twice
        invalid_emails = (
            invalid_emails &
            emails.ne("")
        )

        results["invalid_emails"] = int(
            invalid_emails.sum()
        )


    # ======================================
    # PHONE VALIDATION
    # ======================================

    if "phone" in df.columns:

        phones = (
            df["phone"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        invalid_phones = (
            phones.ne("") &
            (phones.str.len() != 10)
        )

        results["invalid_phones"] = int(
            invalid_phones.sum()
        )


    # ======================================
    # NAME VALIDATION
    # ======================================

    if "name" in df.columns:

        names = (
            df["name"]
            .fillna("")
            .astype(str)
        )

        invalid_names = (
            names.str.strip() == ""
        )

        results["invalid_names"] = int(
            invalid_names.sum()
        )


    # ======================================
    # CITY VALIDATION
    # ======================================

    if "city" in df.columns:

        cities = (
            df["city"]
            .fillna("")
            .astype(str)
        )

        invalid_cities = (
            cities.str.strip() == ""
        )

        results["invalid_cities"] = int(
            invalid_cities.sum()
        )


    return results