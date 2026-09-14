import pandas as pd
import re


# ==========================================
# CLEAN NAME
# ==========================================

def clean_name(value):

    if pd.isna(value):
        return ""

    value = str(value).strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.title()


# ==========================================
# CLEAN EMAIL
# ==========================================

def clean_email(value):

    if pd.isna(value):
        return ""

    return (
        str(value)
        .strip()
        .lower()
    )


# ==========================================
# CLEAN PHONE
# ==========================================

def clean_phone(value):

    if pd.isna(value):
        return ""

    value = str(value).strip()


    # Remove pandas decimal
    if value.endswith(".0"):
        value = value[:-2]


    # Keep digits only
    value = re.sub(
        r"\D",
        "",
        value
    )


    # Remove Indian country code
    if (
        value.startswith("91")
        and len(value) == 12
    ):

        value = value[2:]


    return value


# ==========================================
# CLEAN CITY
# ==========================================

def clean_city(value):

    if pd.isna(value):
        return ""

    value = str(value).strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.title()


# ==========================================
# CLEAN DATAFRAME
# ==========================================

def clean_dataframe(df):

    if not isinstance(
        df,
        pd.DataFrame
    ):

        raise TypeError(
            "clean_dataframe expected "
            "a pandas DataFrame"
        )


    cleaned_df = df.copy()


    # ======================================
    # COLUMN NAMES
    # ======================================

    cleaned_df.columns = (
        cleaned_df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(
            r"\s+",
            "_",
            regex=True
        )
    )


    # ======================================
    # NAME
    # ======================================

    if "name" in cleaned_df.columns:

        cleaned_df["name"] = (
            cleaned_df["name"]
            .apply(clean_name)
        )


    # ======================================
    # EMAIL
    # ======================================

    if "email" in cleaned_df.columns:

        cleaned_df["email"] = (
            cleaned_df["email"]
            .apply(clean_email)
        )


    # ======================================
    # PHONE
    # ======================================

    if "phone" in cleaned_df.columns:

        cleaned_df["phone"] = (
            cleaned_df["phone"]
            .apply(clean_phone)
        )


    # ======================================
    # CITY
    # ======================================

    if "city" in cleaned_df.columns:

        cleaned_df["city"] = (
            cleaned_df["city"]
            .apply(clean_city)
        )


    return cleaned_df