from flask import Flask, jsonify, request, render_template, send_file
from werkzeug.utils import secure_filename

import os
import math
import pandas as pd
import numpy as np

from services.validator import load_data, validate_data
from services.duplicate_detector import find_duplicates
from services.quality_scorer import calculate_quality_score
from services.database import get_connection, initialize_database
from services.cleaner import clean_dataframe


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

CLEANED_FOLDER = os.path.join(
    BASE_DIR,
    "cleaned"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CLEANED_FOLDER"] = CLEANED_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    CLEANED_FOLDER,
    exist_ok=True
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# JSON CONVERSION HELPERS
# ============================================================

def safe_json_value(value):
    """
    Convert Pandas / NumPy values into normal Python
    values that Flask can safely convert to JSON.
    """

    if value is None:
        return ""

    # NumPy integer such as np.int64
    if isinstance(value, np.integer):
        return int(value)

    # NumPy float such as np.float64
    if isinstance(value, np.floating):

        value = float(value)

        if math.isnan(value) or math.isinf(value):
            return ""

        return value

    # NumPy boolean
    if isinstance(value, np.bool_):
        return bool(value)

    # Pandas missing values
    try:

        if pd.isna(value):
            return ""

    except (TypeError, ValueError):
        pass

    # Python float
    if isinstance(value, float):

        if math.isnan(value) or math.isinf(value):
            return ""

        return value

    # Python integer
    if isinstance(value, int):
        return int(value)

    return value


def make_json_safe(value):
    """
    Recursively convert dictionaries, lists and
    Pandas / NumPy values into JSON-safe values.
    """

    if isinstance(value, dict):

        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):

        return [
            make_json_safe(item)
            for item in value
        ]

    return safe_json_value(value)


def dataframe_to_records(df):
    """
    Convert DataFrame to JSON-safe list of dictionaries.
    """

    records = []

    for record in df.to_dict(
        orient="records"
    ):

        safe_record = {}

        for key, value in record.items():

            safe_record[str(key)] = (
                safe_json_value(value)
            )

        records.append(
            safe_record
        )

    return records


# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

def normalize_column_names(df):

    result = df.copy()

    result.columns = (
        result.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(
            r"\s+",
            "_",
            regex=True
        )
    )

    return result


# ============================================================
# COUNT COLUMN CHANGES
# ============================================================

def count_column_changes(
    original_df,
    cleaned_df,
    column
):

    original = normalize_column_names(
        original_df
    )

    cleaned = normalize_column_names(
        cleaned_df
    )

    if column not in original.columns:
        return 0

    if column not in cleaned.columns:
        return 0

    original_values = (
        original[column]
        .fillna("")
        .astype(str)
        .reset_index(drop=True)
    )

    cleaned_values = (
        cleaned[column]
        .fillna("")
        .astype(str)
        .reset_index(drop=True)
    )

    length = min(
        len(original_values),
        len(cleaned_values)
    )

    if length == 0:
        return 0

    changes = (
        original_values.iloc[:length].values
        != cleaned_values.iloc[:length].values
    )

    return int(
        changes.sum()
    )


# ============================================================
# BUILD CLEANING PREVIEW
# ============================================================

def build_cleaning_preview(
    original_df,
    cleaned_df
):

    original = normalize_column_names(
        original_df
    )

    cleaned = normalize_column_names(
        cleaned_df
    )

    preview = []

    fields = [
        "name",
        "email",
        "phone",
        "city"
    ]

    for field in fields:

        if field not in original.columns:
            continue

        if field not in cleaned.columns:
            continue

        original_values = (
            original[field]
            .fillna("")
            .astype(str)
            .reset_index(drop=True)
        )

        cleaned_values = (
            cleaned[field]
            .fillna("")
            .astype(str)
            .reset_index(drop=True)
        )

        length = min(
            len(original_values),
            len(cleaned_values)
        )

        for i in range(length):

            before = original_values.iloc[i]
            after = cleaned_values.iloc[i]

            if before != after:

                preview.append({

                    "field": field,

                    "before": before,

                    "after": after

                })

            if len(preview) >= 50:
                return preview

    return preview


# ============================================================
# EMAIL VALIDATION
# ============================================================

def is_valid_email(value):

    if value is None:
        return False

    value = str(value).strip()

    if value == "":
        return False

    pattern = (
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    import re

    return bool(
        re.match(
            pattern,
            value
        )
    )


# ============================================================
# PHONE VALIDATION
# ============================================================

def is_valid_phone(value):

    if value is None:
        return False

    value = str(value).strip()

    if value == "":
        return False

    import re

    digits = re.sub(
        r"\D",
        "",
        value
    )

    # Remove Indian country code
    if (
        digits.startswith("91")
        and len(digits) == 12
    ):
        digits = digits[2:]

    return len(digits) == 10


# ============================================================
# BUILD DETAILED ISSUES
# ============================================================

def build_issue_list(
    df,
    duplicates
):

    issues = []

    # ========================================================
    # MISSING VALUES
    # ========================================================

    for index, row in df.iterrows():

        customer_id = safe_json_value(
            row.get(
                "customer_id",
                index + 1
            )
        )

        name = safe_json_value(
            row.get(
                "name",
                ""
            )
        )

        email = safe_json_value(
            row.get(
                "email",
                ""
            )
        )

        phone = safe_json_value(
            row.get(
                "phone",
                ""
            )
        )

        city = safe_json_value(
            row.get(
                "city",
                ""
            )
        )

        # ----------------------------------------------------
        # Missing Name
        # ----------------------------------------------------

        if "name" in df.columns:

            value = row.get("name")

            if (
                pd.isna(value)
                or str(value).strip() == ""
            ):

                issues.append({

                    "record_index":
                        int(index),

                    "customer_id":
                        customer_id,

                    "name":
                        name,

                    "email":
                        email,

                    "phone":
                        phone,

                    "city":
                        city,

                    "issue_type":
                        "Missing Values",

                    "field":
                        "name",

                    "severity":
                        "Medium",

                    "description":
                        "Name is missing.",

                    "suggestion":
                        "Add the customer's name."

                })

        # ----------------------------------------------------
        # Missing Email
        # ----------------------------------------------------

        if "email" in df.columns:

            value = row.get("email")

            if (
                pd.isna(value)
                or str(value).strip() == ""
            ):

                issues.append({

                    "record_index":
                        int(index),

                    "customer_id":
                        customer_id,

                    "name":
                        name,

                    "email":
                        email,

                    "phone":
                        phone,

                    "city":
                        city,

                    "issue_type":
                        "Missing Values",

                    "field":
                        "email",

                    "severity":
                        "Medium",

                    "description":
                        "Email address is missing.",

                    "suggestion":
                        "Add an email address."

                })

        # ----------------------------------------------------
        # Missing Phone
        # ----------------------------------------------------

        if "phone" in df.columns:

            value = row.get("phone")

            if (
                pd.isna(value)
                or str(value).strip() == ""
            ):

                issues.append({

                    "record_index":
                        int(index),

                    "customer_id":
                        customer_id,

                    "name":
                        name,

                    "email":
                        email,

                    "phone":
                        phone,

                    "city":
                        city,

                    "issue_type":
                        "Missing Values",

                    "field":
                        "phone",

                    "severity":
                        "Medium",

                    "description":
                        "Phone number is missing.",

                    "suggestion":
                        "Add a valid 10-digit phone number."

                })

        # ----------------------------------------------------
        # Missing City
        # ----------------------------------------------------

        if "city" in df.columns:

            value = row.get("city")

            if (
                pd.isna(value)
                or str(value).strip() == ""
            ):

                issues.append({

                    "record_index":
                        int(index),

                    "customer_id":
                        customer_id,

                    "name":
                        name,

                    "email":
                        email,

                    "phone":
                        phone,

                    "city":
                        city,

                    "issue_type":
                        "Missing Values",

                    "field":
                        "city",

                    "severity":
                        "Medium",

                    "description":
                        "City is missing.",

                    "suggestion":
                        "Add the customer's city."

                })

    # ========================================================
    # INVALID EMAILS
    # ========================================================

    if "email" in df.columns:

        for index, row in df.iterrows():

            value = row.get("email")

            if pd.isna(value):
                continue

            value = str(value).strip()

            if value == "":
                continue

            if not is_valid_email(value):

                issues.append({

                    "record_index":
                        int(index),

                    "customer_id":
                        safe_json_value(
                            row.get(
                                "customer_id",
                                index + 1
                            )
                        ),

                    "name":
                        safe_json_value(
                            row.get(
                                "name",
                                ""
                            )
                        ),

                    "email":
                        value,

                    "phone":
                        safe_json_value(
                            row.get(
                                "phone",
                                ""
                            )
                        ),

                    "city":
                        safe_json_value(
                            row.get(
                                "city",
                                ""
                            )
                        ),

                    "issue_type":
                        "Invalid Emails",

                    "field":
                        "email",

                    "severity":
                        "High",

                    "description":
                        "Email address has an invalid format.",

                    "suggestion":
                        "Correct the email format, for example name@example.com."

                })

    # ========================================================
    # INVALID PHONES
    # ========================================================

    if "phone" in df.columns:

        for index, row in df.iterrows():

            value = row.get("phone")

            if pd.isna(value):
                continue

            value = str(value).strip()

            if value == "":
                continue

            if not is_valid_phone(value):

                issues.append({

                    "record_index":
                        int(index),

                    "customer_id":
                        safe_json_value(
                            row.get(
                                "customer_id",
                                index + 1
                            )
                        ),

                    "name":
                        safe_json_value(
                            row.get(
                                "name",
                                ""
                            )
                        ),

                    "email":
                        safe_json_value(
                            row.get(
                                "email",
                                ""
                            )
                        ),

                    "phone":
                        value,

                    "city":
                        safe_json_value(
                            row.get(
                                "city",
                                ""
                            )
                        ),

                    "issue_type":
                        "Invalid Phones",

                    "field":
                        "phone",

                    "severity":
                        "High",

                    "description":
                        "Phone number is not a valid 10-digit number.",

                    "suggestion":
                        "Enter a valid 10-digit phone number."

                })

    # ========================================================
    # DUPLICATES
    # ========================================================

    if (
        duplicates is not None
        and not duplicates.empty
    ):

        for index, row in duplicates.iterrows():

            issues.append({

                "record_index":
                    int(index),

                "customer_id":
                    safe_json_value(
                        row.get(
                            "customer_id",
                            index + 1
                        )
                    ),

                "name":
                    safe_json_value(
                        row.get(
                            "name",
                            ""
                        )
                    ),

                "email":
                    safe_json_value(
                        row.get(
                            "email",
                            ""
                        )
                    ),

                "phone":
                    safe_json_value(
                        row.get(
                            "phone",
                            ""
                        )
                    ),

                "city":
                    safe_json_value(
                        row.get(
                            "city",
                            ""
                        )
                    ),

                "issue_type":
                    "Duplicate Records",

                "field":
                    "record",

                "severity":
                    "High",

                "description":
                    "This record appears to be a duplicate.",

                "suggestion":
                    "Review the duplicate records and keep the correct record."

            })

    return issues


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# ANALYZE DATASET
# ============================================================

@app.route(
    "/api/upload",
    methods=["POST"]
)
def upload_file():

    try:

        # ----------------------------------------------------
        # CHECK FILE
        # ----------------------------------------------------

        if "file" not in request.files:

            return jsonify({
                "error":
                    "No file uploaded"
            }), 400

        file = request.files["file"]

        if file.filename == "":

            return jsonify({
                "error":
                    "No file selected"
            }), 400

        if not file.filename.lower().endswith(".csv"):

            return jsonify({
                "error":
                    "Only CSV files are allowed"
            }), 400

        # ----------------------------------------------------
        # SAVE FILE
        # ----------------------------------------------------

        filename = secure_filename(
            file.filename
        )

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(
            file_path
        )

        # ----------------------------------------------------
        # LOAD DATA
        # ----------------------------------------------------

        df = load_data(
            file_path
        )

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        validation_results = validate_data(
            df
        )

        # ----------------------------------------------------
        # DUPLICATES
        # ----------------------------------------------------

        try:

            duplicates = find_duplicates(
                df
            )

            duplicate_records = len(
                duplicates
            )

        except Exception as error:

            print(
                "Duplicate detection error:",
                error
            )

            duplicates = pd.DataFrame()

            duplicate_records = 0

        # ----------------------------------------------------
        # QUALITY SCORE
        # ----------------------------------------------------

        quality_score = calculate_quality_score(

            total_records=
                validation_results[
                    "total_records"
                ],

            missing_values=
                validation_results[
                    "missing_values"
                ],

            invalid_emails=
                validation_results[
                    "invalid_emails"
                ],

            invalid_phones=
                validation_results[
                    "invalid_phones"
                ],

            duplicate_records=
                duplicate_records
        )

        # Make score definitely Python float
        quality_score = float(
            quality_score
        )

        # ----------------------------------------------------
        # DETAILED ISSUES
        # ----------------------------------------------------

        issues = build_issue_list(
            df,
            duplicates
        )

        # ====================================================
        # DATABASE
        # ====================================================

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO datasets
            (
                filename,
                total_records,
                quality_score
            )
            VALUES (?, ?, ?)
            """,
            (
                filename,
                int(
                    validation_results[
                        "total_records"
                    ]
                ),
                quality_score
            )
        )

        dataset_id = cursor.lastrowid

        # ----------------------------------------------------
        # SAVE RECORDS
        # ----------------------------------------------------

        for _, row in df.iterrows():

            def db_value(column):

                value = row.get(
                    column,
                    ""
                )

                if pd.isna(value):
                    return None

                # Convert NumPy values before SQLite
                if isinstance(
                    value,
                    np.integer
                ):
                    return int(value)

                if isinstance(
                    value,
                    np.floating
                ):
                    return float(value)

                return value

            customer_id = db_value(
                "customer_id"
            )

            if customer_id is None:

                customer_id = ""

            else:

                customer_id = str(
                    customer_id
                )

            cursor.execute(
                """
                INSERT INTO records
                (
                    dataset_id,
                    customer_id,
                    name,
                    email,
                    phone,
                    city,
                    latitude,
                    longitude
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dataset_id,
                    customer_id,
                    db_value("name"),
                    db_value("email"),
                    db_value("phone"),
                    db_value("city"),
                    db_value("latitude"),
                    db_value("longitude")
                )
            )

        # ----------------------------------------------------
        # SAVE ISSUE SUMMARY
        # ----------------------------------------------------

        issue_values = [

            (
                validation_results[
                    "missing_values"
                ],
                "Missing Values"
            ),

            (
                validation_results[
                    "invalid_emails"
                ],
                "Invalid Emails"
            ),

            (
                validation_results[
                    "invalid_phones"
                ],
                "Invalid Phones"
            ),

            (
                duplicate_records,
                "Duplicate Records"
            )
        ]

        for count, issue_type in issue_values:

            count = int(count)

            if count > 0:

                cursor.execute(
                    """
                    INSERT INTO issues
                    (
                        dataset_id,
                        issue_type,
                        description
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        dataset_id,
                        issue_type,
                        f"{count} {issue_type.lower()} detected"
                    )
                )

        connection.commit()

        connection.close()

        # ====================================================
        # DUPLICATES FOR FRONTEND
        # ====================================================

        if (
            duplicates is not None
            and not duplicates.empty
        ):

            duplicate_data = (
                duplicates
                .drop(
                    columns=[
                        "normalized_name",
                        "normalized_email"
                    ],
                    errors="ignore"
                )
            )

            duplicate_data = dataframe_to_records(
                duplicate_data
            )

        else:

            duplicate_data = []

        # ====================================================
        # LOCATIONS
        # ====================================================

        locations = []

        if (
            "latitude" in df.columns
            and
            "longitude" in df.columns
        ):

            location_columns = [
                column
                for column in [
                    "customer_id",
                    "name",
                    "city",
                    "latitude",
                    "longitude"
                ]
                if column in df.columns
            ]

            location_df = df[
                location_columns
            ].copy()

            location_df = location_df.dropna(
                subset=[
                    "latitude",
                    "longitude"
                ]
            )

            locations = dataframe_to_records(
                location_df
            )

        # ====================================================
        # ISSUE SUMMARY
        # ====================================================

        issue_summary = {

            "total":
                int(len(issues)),

            "missing_values":
                int(
                    sum(
                        1
                        for issue in issues
                        if issue["issue_type"]
                        == "Missing Values"
                    )
                ),

            "invalid_emails":
                int(
                    sum(
                        1
                        for issue in issues
                        if issue["issue_type"]
                        == "Invalid Emails"
                    )
                ),

            "invalid_phones":
                int(
                    sum(
                        1
                        for issue in issues
                        if issue["issue_type"]
                        == "Invalid Phones"
                    )
                ),

            "duplicates":
                int(
                    sum(
                        1
                        for issue in issues
                        if issue["issue_type"]
                        == "Duplicate Records"
                    )
                )
        }

        # ====================================================
        # RESPONSE
        # ====================================================

        response_data = {

            "message":
                "File analyzed successfully",

            "filename":
                filename,

            "dataset_id":
                dataset_id,

            "validation":
                validation_results,

            "duplicate_records":
                duplicate_records,

            "duplicates":
                duplicate_data,

            "locations":
                locations,

            "quality_score":
                quality_score,

            "issues":
                issues,

            "issue_summary":
                issue_summary,

            "cleaning": {

                "status":
                    "Not cleaned",

                "before_records":
                    len(df),

                "after_records":
                    len(df),

                "records_changed":
                    0
            }
        }

        return jsonify(
            make_json_safe(
                response_data
            )
        )

    except Exception as error:

        print(
            "\n========== ANALYSIS ERROR =========="
        )

        print(
            repr(error)
        )

        print(
            "====================================\n"
        )

        return jsonify({

            "error":
                str(error)

        }), 500


# ============================================================
# CLEAN & STANDARDIZE DATASET
# ============================================================

@app.route(
    "/api/clean",
    methods=["POST"]
)
def clean_file():

    try:

        # ----------------------------------------------------
        # CHECK FILE
        # ----------------------------------------------------

        if "file" not in request.files:

            return jsonify({
                "error":
                    "No file uploaded"
            }), 400

        file = request.files["file"]

        if file.filename == "":

            return jsonify({
                "error":
                    "No file selected"
            }), 400

        if not file.filename.lower().endswith(".csv"):

            return jsonify({
                "error":
                    "Only CSV files are allowed"
            }), 400

        # ----------------------------------------------------
        # SAVE ORIGINAL
        # ----------------------------------------------------

        filename = secure_filename(
            file.filename
        )

        original_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(
            original_path
        )

        # ----------------------------------------------------
        # LOAD ORIGINAL
        # ----------------------------------------------------

        original_df = load_data(
            original_path
        )

        # ----------------------------------------------------
        # CLEAN DATA
        # ----------------------------------------------------

        cleaned_df = clean_dataframe(
            original_df.copy()
        )

        # ====================================================
        # RECORD COUNTS
        # ====================================================

        before_records = int(
            len(original_df)
        )

        after_records = int(
            len(cleaned_df)
        )

        # ====================================================
        # COLUMN CHANGES
        # ====================================================

        names_standardized = count_column_changes(
            original_df,
            cleaned_df,
            "name"
        )

        emails_standardized = count_column_changes(
            original_df,
            cleaned_df,
            "email"
        )

        phones_standardized = count_column_changes(
            original_df,
            cleaned_df,
            "phone"
        )

        cities_standardized = count_column_changes(
            original_df,
            cleaned_df,
            "city"
        )

        # ====================================================
        # RECORDS CHANGED
        # ====================================================

        records_changed = 0

        original_compare = normalize_column_names(
            original_df
        )

        cleaned_compare = normalize_column_names(
            cleaned_df
        )

        common_columns = [
            column
            for column in cleaned_compare.columns
            if column in original_compare.columns
        ]

        if common_columns:

            original_values = (
                original_compare[
                    common_columns
                ]
                .fillna("")
                .astype(str)
                .reset_index(drop=True)
            )

            cleaned_values = (
                cleaned_compare[
                    common_columns
                ]
                .fillna("")
                .astype(str)
                .reset_index(drop=True)
            )

            length = min(
                len(original_values),
                len(cleaned_values)
            )

            if length > 0:

                row_changes = (
                    original_values.iloc[:length]
                    != cleaned_values.iloc[:length]
                ).any(axis=1)

                records_changed = int(
                    row_changes.sum()
                )

        # ====================================================
        # BEFORE / AFTER PREVIEW
        # ====================================================

        preview = build_cleaning_preview(
            original_df,
            cleaned_df
        )

        # ====================================================
        # SAVE CLEANED CSV
        # ====================================================

        cleaned_filename = (
            "cleaned_"
            + filename
        )

        cleaned_path = os.path.join(
            app.config["CLEANED_FOLDER"],
            cleaned_filename
        )

        cleaned_df.to_csv(
            cleaned_path,
            index=False
        )

        # ====================================================
        # CLEANING SUMMARY
        # ====================================================

        cleaning_summary = {

            "status":
                "Completed",

            "before_records":
                before_records,

            "after_records":
                after_records,

            "records_changed":
                records_changed,

            "records_processed":
                before_records,

            "names_standardized":
                int(names_standardized),

            "emails_standardized":
                int(emails_standardized),

            "phones_standardized":
                int(phones_standardized),

            "cities_standardized":
                int(cities_standardized),

            "columns":
                int(len(cleaned_df.columns)),

            "filename":
                cleaned_filename
        }

        # ====================================================
        # RESPONSE
        # ====================================================

        response_data = {

            "message":
                "Dataset cleaned and standardized successfully.",

            "filename":
                filename,

            "cleaned_filename":
                cleaned_filename,

            "cleaning":
                cleaning_summary,

            "cleaning_summary":
                cleaning_summary,

            "before_records":
                before_records,

            "after_records":
                after_records,

            "records_changed":
                records_changed,

            "records_processed":
                before_records,

            "names_standardized":
                int(names_standardized),

            "emails_standardized":
                int(emails_standardized),

            "phones_standardized":
                int(phones_standardized),

            "cities_standardized":
                int(cities_standardized),

            "preview":
                preview,

            "data":
                dataframe_to_records(
                    cleaned_df
                )
        }

        return jsonify(
            make_json_safe(
                response_data
            )
        )

    except Exception as error:

        print(
            "\n========== CLEANING ERROR =========="
        )

        print(
            repr(error)
        )

        print(
            "====================================\n"
        )

        return jsonify({

            "error":
                str(error)

        }), 500


# ============================================================
# DOWNLOAD CLEANED DATASET
# ============================================================

@app.route(
    "/api/download/<filename>",
    methods=["GET"]
)
def download_cleaned_file(
    filename
):

    safe_filename = secure_filename(
        filename
    )

    file_path = os.path.join(
        app.config["CLEANED_FOLDER"],
        safe_filename
    )

    if not os.path.exists(
        file_path
    ):

        return jsonify({

            "error":
                "Cleaned file not found."

        }), 404

    return send_file(

        file_path,

        as_attachment=True,

        download_name=safe_filename,

        mimetype="text/csv"
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )