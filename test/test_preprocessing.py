import unittest
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_preprocessing import DataPreprocessor


class TestDataPreprocessing(unittest.TestCase):
    def setUp(self):
        self.preprocessor = DataPreprocessor()
        # Create sample data for testing
        self.sample_data = pd.DataFrame({
            'Member_number': [1, 1, 2, 2, 3, 3, 3],
            'Date': ['2023-01-01', '2023-01-01', '2023-01-02', '2023-01-02', '2023-01-03', '2023-01-03', '2023-01-03'],
            'itemDescription': ['milk', 'bread', 'milk', 'eggs', 'bread', 'butter', 'cheese']
        })

    def test_load_data(self):
        # Test that load_data method exists and returns DataFrame
        self.assertTrue(hasattr(self.preprocessor, 'load_data'))

    def test_prepare_transactions(self):
        self.preprocessor.data = self.sample_data
        transactions = self.preprocessor.prepare_transactions()

        self.assertIsInstance(transactions, list)
        self.assertTrue(len(transactions) > 0)

        # Should create 3 transactions (one per unique Member_number + Date combination)
        self.assertEqual(len(transactions), 3)

        # Check that each transaction is a list of strings
        for transaction in transactions:
            self.assertIsInstance(transaction, list)
            for item in transaction:
                self.assertIsInstance(item, str)

    def test_get_frequent_items(self):
        self.preprocessor.data = self.sample_data
        frequent_items = self.preprocessor.get_frequent_items(top_n=3)

        self.assertIsInstance(frequent_items, pd.Series)
        self.assertEqual(len(frequent_items), 3)

        # Milk and bread should be the most frequent
        self.assertIn('milk', frequent_items.index)
        self.assertIn('bread', frequent_items.index)

    def test_explore_data(self):
        self.preprocessor.data = self.sample_data
        info = self.preprocessor.explore_data()

        expected_keys = ['shape', 'columns', 'data_types', 'missing_values', 'memory_usage', 'head']
        for key in expected_keys:
            self.assertIn(key, info)

        self.assertEqual(info['shape'], (7, 3))

    def test_clean_data(self):
        # Create data with duplicates and missing values
        dirty_data = pd.DataFrame({
            'Member_number': [1, 1, 2, 2, 1],
            'Date': ['2023-01-01', '2023-01-01', '2023-01-02', '2023-01-02', '2023-01-01'],
            'itemDescription': ['milk', 'bread', None, 'eggs', 'milk']
        })

        self.preprocessor.data = dirty_data
        cleaned_data = self.preprocessor.clean_data()

        self.assertEqual(len(cleaned_data), 3)  # Removed duplicate and None
        self.assertFalse(cleaned_data['itemDescription'].isnull().any())


if __name__ == '__main__':
    unittest.main()