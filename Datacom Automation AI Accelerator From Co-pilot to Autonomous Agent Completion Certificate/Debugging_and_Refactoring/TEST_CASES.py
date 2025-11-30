#!/usr/bin/env python3
"""
Unit tests to reproduce the AttributeError bug in export_customer_data.

The bug occurs when self.customers contains malformed data structures
that cause a 'dict' object has no attribute 'keys' error during export.
"""

import unittest
import tempfile
import os
import json
from process_data import DataProcessor


class TestExportCustomerDataBug(unittest.TestCase):
    """Test cases to reproduce the export_customer_data AttributeError bug."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = DataProcessor("dummy.csv")
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(self.temp_dir)

    def test_export_with_malformed_customer_structure(self):
        """
        Reproduce the bug: export fails when a customer value is not a simple dict.
        
        Root cause: The export_customer_data method calls:
            fieldnames = ["customer_id"] + list(next(iter(self.customers.values())).keys())
        
        The error occurs when the first customer value returned by iter().next()
        is not a dict but some other object type (e.g., a list or string), causing
        .keys() to fail with AttributeError: 'list' object has no attribute 'keys'.
        
        This test replaces a customer value with a non-dict object to trigger the bug.
        The export_customer_data function catches this exception, logs it, and returns False.
        """
        # Populate with normal customer data first
        self.processor.customers = {
            "C001": {
                "name": "Alice",
                "email": "alice@example.com",
                "join_date": "2023-01-01",
                "total_spent": 100.0,
                "transaction_count": 5,
            },
            "C002": {
                "name": "Bob",
                "email": "bob@example.com",
                "join_date": "2023-02-01",
                "total_spent": 150.0,
                "transaction_count": 8,
            },
        }

        # Corrupt the structure: replace a customer dict with a list
        # This creates a situation where .keys() will fail because lists don't have .keys()
        self.processor.customers["C001"] = ["Alice", "alice@example.com", "2023-01-01"]

        # Attempt to export as CSV - this should trigger the bug on fieldname extraction
        output_file = os.path.join(self.temp_dir, "customers_export.csv")
        
        # The bug manifests: export_customer_data catches the exception and returns False
        result = self.processor.export_customer_data(output_file, format="csv")
        self.assertFalse(result, "export_customer_data should return False when AttributeError occurs")

    def test_export_csv_with_dict_fieldnames(self):
        """
        Reproduce the bug at CSV fieldname extraction stage.
        
        When a customer value is a string instead of a dict,
        the fieldnames extraction step fails because strings don't have .keys().
        The export_customer_data function catches the AttributeError and returns False.
        """
        # Populate processor with one corrupted entry (string instead of dict)
        self.processor.customers = {
            "C001": "Alice",  # Corrupt: a string instead of a dict
            "C002": {
                "name": "Bob",
                "email": "bob@example.com",
                "join_date": "2023-02-01",
                "total_spent": 150.0,
                "transaction_count": 8,
            }
        }

        output_file = os.path.join(self.temp_dir, "customers_export_malformed.csv")

        # This should fail and return False (exception is caught internally)
        result = self.processor.export_customer_data(output_file, format="csv")
        self.assertFalse(result, "export_customer_data should return False when AttributeError occurs")

    def test_export_json_with_non_dict_values(self):
        """
        Test JSON export with malformed structure.
        
        When customer data is not properly formed (e.g., a customer value
        is a string), the JSON export will serialize it as-is without calling
        .keys(), but the CSV export (if attempted) would fail. This test
        validates that JSON export gracefully handles such data.
        """
        # Create processor with a customer entry that is a string
        self.processor.customers = {
            "C001": "Alice",  # Non-dict value
            "C002": {
                "name": "Bob",
                "email": "bob@example.com",
                "join_date": "2023-02-01",
                "total_spent": 150.0,
                "transaction_count": 8,
            }
        }

        output_file = os.path.join(self.temp_dir, "customers_export_invalid.json")

        # JSON export will succeed because json.dump() doesn't call .keys()
        # It just serializes the dict structure as-is
        result = self.processor.export_customer_data(output_file, format="json")
        self.assertTrue(result, "JSON export should succeed even with mixed data types")
        self.assertTrue(os.path.exists(output_file), "JSON output file should be created")

    def test_normal_export_succeeds(self):
        """
        Control test: verify that normal, well-formed data exports successfully.
        
        This ensures our test infrastructure works and that the bug is specific
        to malformed data structures.
        """
        # Populate with properly-formed customer data
        self.processor.customers = {
            "C001": {
                "name": "Alice",
                "email": "alice@example.com",
                "join_date": "2023-01-01",
                "total_spent": 100.0,
                "transaction_count": 5,
            },
            "C002": {
                "name": "Bob",
                "email": "bob@example.com",
                "join_date": "2023-02-01",
                "total_spent": 150.0,
                "transaction_count": 8,
            },
        }

        # CSV export should succeed
        csv_output = os.path.join(self.temp_dir, "customers_normal.csv")
        result = self.processor.export_customer_data(csv_output, format="csv")
        self.assertTrue(result)
        self.assertTrue(os.path.exists(csv_output))

        # JSON export should succeed
        json_output = os.path.join(self.temp_dir, "customers_normal.json")
        result = self.processor.export_customer_data(json_output, format="json")
        self.assertTrue(result)
        self.assertTrue(os.path.exists(json_output))


if __name__ == "__main__":
    unittest.main()
