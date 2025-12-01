# 📊 Data Processing Utility — Overview

This project contains a Python-based data processing system designed to ingest customer and transaction CSV files, compute business analytics, and export structured reports. It follows an object-oriented architecture and includes logging, error handling, and export utilities.

The core script (process_data.py) loads customer profiles, processes financial transactions, calculates aggregated business metrics, performs substring search, and exports reports in formats such as CSV and JSON.

The repository also contains unit tests and bug analysis documentation (e.g., DEBUG_LOG.md) capturing the debugging and refactoring process.


## 🐞 Debugging & Improvements
The DEBUG_LOG.md details a full debugging session covering a failure in the export_customer_data() function:

## Root Cause
An unsafe .keys() call on customer data during CSV field extraction caused:

 'dict' object has no attribute 'keys'
 
The error surfaced when malformed or unexpected customer records were encountered.

## Fix Implemented
- The function was refactored to:
- Use explicit, fixed fieldnames
- Add data validation checks
- Improve performance using direct dictionary lookups
- Gracefully return errors instead of crashing

## Testing
A dedicated test suite (TEST_CASES.py) was created to:
- Reproduce the bug
- Validate the fix
- Confirm correct behavior for malformed and valid datasets
All tests now pass successfully.


## 💡 Future Improvements
- Add data validation for CSV schemas
- Parameterize input/output paths
- Introduce caching for metrics
- Add more robust logging (file handlers, debug levels)
- Support additional export formats (Excel, SQL)
