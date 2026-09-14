from services.validator import load_data, validate_data
from services.duplicate_detector import find_duplicates
from services.quality_scorer import calculate_quality_score


df = load_data("data/customers.csv")

# Validation
results = validate_data(df)

# Duplicate detection
duplicates = find_duplicates(df)

# Number of duplicate records
duplicate_records = len(duplicates)

# Quality score
score = calculate_quality_score(
    total_records=results["total_records"],
    missing_values=results["missing_values"],
    invalid_emails=results["invalid_emails"],
    invalid_phones=results["invalid_phones"],
    duplicate_records=duplicate_records
)


print("Validation Results:")
print(results)

print("\nDuplicate Records:")
print(duplicates)

print("\nData Quality Score:")
print(score)