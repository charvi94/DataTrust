# DataTrust
## Screenshots

### Dashboard

![DataTrust Dashboard](screenshots/dashboard.png)

### Data Quality Analysis

![Data Quality Analysis](screenshots/analysis.png)

### Data Cleaning & Standardization

![Data Cleaning & Standardization](screenshots/cleaning.png)

### Data Quality Insights

![Data Quality Insights](screenshots/insights.png)

## Smart Data Quality & Integrity Platform

DataTrust is a web-based data quality and integrity platform that helps users analyze, validate, clean, standardize, and visualize datasets.

The application allows users to upload CSV datasets, identify data-quality issues, detect duplicate records, calculate a data-quality score, visualize geographic information, and download a cleaned version of the dataset.

---

## Features

- CSV dataset upload
- Data-quality analysis
- Missing-value detection
- Email validation
- Phone-number validation
- Duplicate-record detection
- Data-quality score calculation
- Data-quality issue summary
- Before → After cleaning preview
- Name standardization
- Email standardization
- Phone-number standardization
- City standardization
- Geographic visualization using Location Intelligence
- Cleaned dataset download
- Interactive dashboard
- Database integration
- Data-quality insights and visualization

---

## Tech Stack

### Frontend

- HTML
- CSS
- JavaScript
- Leaflet.js
- Chart.js

### Backend

- Python
- Flask
- Pandas

### Data & Validation

- CSV
- Regular Expressions
- Data validation
- Data cleaning and standardization

### Database

- SQLite

---

## Project Structure

```text
DataTrust/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── customers.csv
│
├── services/
│   ├── cleaner.py
│   ├── database.py
│   ├── duplicate_detector.py
│   ├── quality_scorer.py
│   └── validator.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── dashboard.js
│
├── templates/
│   └── index.html
│
├── uploads/
│   ├── customers.csv
│   └── ...
│
├── cleaned/
│   └── ...
│
├── datatrust.db
│
├── db_test.py
├── test.py
└── test_cleaner.py
```

---

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate into the project

```bash
cd DataTrust
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 5. Install the required packages

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the Flask application:

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000/
```

Open the address in your browser.

---

## Using DataTrust

### Step 1 — Upload Dataset

Upload a CSV dataset using the file-upload section.

The application accepts CSV files containing customer or other structured records.

### Step 2 — Analyze Dataset

Click:

```text
Analyze Dataset
```

The application analyzes the uploaded dataset and identifies potential data-quality issues.

### Step 3 — Review Analysis Results

The dashboard displays:

- Total records
- Missing values
- Invalid emails
- Invalid phones
- Duplicate records
- Data-quality score

### Step 4 — Review Data-Quality Issues

The application provides a detailed summary of detected issues, including:

- Missing values
- Invalid emails
- Invalid phones
- Duplicate records

### Step 5 — Review Duplicate Records

Detected duplicate records are displayed in a dedicated table.

This helps users identify repeated or potentially redundant records in the dataset.

### Step 6 — View Location Intelligence

The Location Intelligence section provides a geographic visualization of records using available latitude and longitude information.

### Step 7 — Clean & Standardize Dataset

Click:

```text
Clean & Standardize Dataset
```

The application processes the uploaded dataset and standardizes supported fields.

### Step 8 — Review Cleaning Summary

The dashboard displays:

- Original records
- Cleaned records
- Records modified
- Cleaning status

It also provides a Before → After Preview showing examples of modified values.

### Step 9 — Review Cleaned Dataset

The cleaned dataset is displayed directly in the dashboard.

### Step 10 — Download Cleaned Dataset

Users can download the cleaned dataset for further use.

---

## Data Cleaning & Standardization

DataTrust performs several data-cleaning and standardization operations.

### Names

Names are normalized by:

- Removing unnecessary whitespace
- Standardizing capitalization
- Converting names to title case

Example:

```text
RAHUL SHARMA
```

becomes:

```text
Rahul Sharma
```

---

### Emails

Email addresses are normalized by:

- Removing unnecessary whitespace
- Converting email addresses to lowercase

Example:

```text
RAHUL@GMAIL.COM
```

becomes:

```text
rahul@gmail.com
```

---

### Phone Numbers

Phone numbers are standardized by:

- Removing unnecessary formatting characters
- Keeping numeric digits
- Handling common `+91` / `91` country-code representations
- Handling values that may be represented as decimal numbers in CSV files

Example:

```text
+91 98765-43210
```

is standardized to:

```text
9876543210
```

---

### Cities

City values are normalized by:

- Removing unnecessary whitespace
- Standardizing capitalization

Example:

```text
delhi
```

becomes:

```text
Delhi
```

---

## Data Quality Analysis

DataTrust evaluates the uploaded dataset using multiple quality checks.

### Missing Values

Identifies empty or missing values within the dataset.

### Invalid Emails

Checks email fields for invalid or improperly formatted email addresses.

### Invalid Phones

Checks phone fields for invalid phone-number formats.

### Duplicate Records

Identifies records that contain duplicate customer information.

### Data Quality Score

The platform calculates an overall data-quality score based on the detected issues in the dataset.

The score is presented visually on the dashboard along with a corresponding quality classification.

---

## Before → After Preview

The Before → After Preview allows users to see how the cleaning process changes individual values.

For example:

| Field | Before | After |
|---|---|---|
| Name | RAHUL SHARMA | Rahul Sharma |
| Email | RAHUL@GMAIL.COM | rahul@gmail.com |

This makes the standardization process transparent to the user.

---

## Location Intelligence

DataTrust includes a Location Intelligence section that visualizes geographic records on an interactive map.

Records containing latitude and longitude information can be displayed geographically, helping users understand the spatial distribution of their data.

---

## Data Visualization

The dashboard provides visual representations of data-quality information to make the analysis easier to understand.

The project uses:

- Chart.js for dashboard visualizations
- Leaflet.js for geographic visualization

---

## Database

DataTrust uses SQLite for database functionality.

The project contains:

```text
datatrust.db
```

Database-related functionality is implemented through:

```text
services/database.py
```

---

## Testing

The project contains test files for validating core functionality:

```text
test.py
test_cleaner.py
db_test.py
```

These tests help verify data-cleaning and database-related functionality.

---

## Security & Repository Hygiene

Local datasets, generated files, databases, virtual environments, and environment-specific files are excluded from version control using `.gitignore`.

This helps prevent local customer data and generated files from being accidentally committed to the public repository.

Before pushing the project to GitHub, verify that sensitive or locally generated files are not included in the Git repository.

---

## Future Enhancements

Possible future improvements include:

- User authentication
- Role-based access control
- Persistent analysis history
- Automated PDF reports
- Advanced anomaly detection
- Additional validation rules
- Data-quality trend analysis
- Cloud deployment
- REST API access
- Database-backed dashboards
- Automated data-quality recommendations
- Improved reporting and analytics

---

## Purpose

DataTrust was developed as a data-quality and integrity project to demonstrate practical skills in:

- Python
- Flask
- Pandas
- JavaScript
- HTML
- CSS
- Data validation
- Data cleaning
- Data standardization
- Data visualization
- Database integration
- Web application development

The project demonstrates how a raw CSV dataset can be analyzed, validated, cleaned, standardized, visualized, and exported through a single web-based platform.

---

## License

This project is developed for educational and portfolio purposes.