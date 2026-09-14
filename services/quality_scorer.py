def calculate_quality_score(
    total_records,
    missing_values,
    invalid_emails,
    invalid_phones,
    duplicate_records
):

    if total_records == 0:
        return 0

    # Calculate issue percentages
    missing_rate = missing_values / total_records
    email_error_rate = invalid_emails / total_records
    phone_error_rate = invalid_phones / total_records
    duplicate_rate = duplicate_records / total_records

    # Weights
    missing_weight = 0.30
    email_weight = 0.20
    phone_weight = 0.20
    duplicate_weight = 0.30

    # Calculate penalties
    penalty = (
        missing_rate * missing_weight
        + email_error_rate * email_weight
        + phone_error_rate * phone_weight
        + duplicate_rate * duplicate_weight
    )

    # Convert into score
    score = (1 - penalty) * 100

    return round(max(score, 0), 2)