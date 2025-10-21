import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any


class DataPreprocessor:
    def __init__(self):
        self.data = None
        self.transactions = None

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load dataset from CSV file"""
        try:
            if hasattr(file_path, 'read'):
                # If it's a file-like object (Streamlit upload)
                self.data = pd.read_csv(file_path)
            else:
                # If it's a file path
                self.data = pd.read_csv(file_path)

            print(f"Dataset loaded successfully with {len(self.data)} rows and {len(self.data.columns)} columns")
            return self.data
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return None

    def explore_data(self) -> Dict[str, Any]:
        """Explore basic information about the dataset"""
        if self.data is None:
            print("No data loaded")
            return {}

        info = {
            'shape': self.data.shape,
            'columns': self.data.columns.tolist(),
            'data_types': self.data.dtypes,
            'missing_values': self.data.isnull().sum(),
            'memory_usage': self.data.memory_usage(deep=True).sum(),
            'head': self.data.head(),
            'describe': self.data.describe(include='all')
        }

        print("=== Dataset Information ===")
        print(f"Shape: {info['shape']}")
        print(f"Columns: {info['columns']}")
        print(f"Memory usage: {info['memory_usage']} bytes")
        print("\n=== Data Types ===")
        print(info['data_types'])
        print("\n=== Missing Values ===")
        print(info['missing_values'])

        return info

    def prepare_transactions(self) -> List[List[str]]:
        """Prepare transactions in the format required for Apriori"""
        if self.data is None:
            print("No data loaded")
            return []

        # Check if required columns exist
        if 'itemDescription' not in self.data.columns:
            print("Error: 'itemDescription' column not found in dataset")
            return []

        # Group items by transaction
        if 'Member_number' in self.data.columns and 'Date' in self.data.columns:
            # Create transaction ID from Member_number and Date
            self.data['Transaction_ID'] = self.data['Member_number'].astype(str) + '_' + self.data['Date']
            transactions = self.data.groupby('Transaction_ID')['itemDescription'].apply(list).tolist()
        elif 'Transaction' in self.data.columns:
            # Use existing Transaction column
            transactions = self.data.groupby('Transaction')['itemDescription'].apply(list).tolist()
        else:
            # If no transaction ID, assume each row is a separate transaction
            print("Warning: No transaction identifier found. Using each row as a separate transaction.")
            transactions = [[item] for item in self.data['itemDescription'].values]

        self.transactions = transactions
        print(f"Prepared {len(transactions)} transactions")

        # Print transaction statistics
        if transactions:
            transaction_lengths = [len(t) for t in transactions]
            print(f"Average items per transaction: {np.mean(transaction_lengths):.2f}")
            print(f"Max items per transaction: {max(transaction_lengths)}")
            print(f"Min items per transaction: {min(transaction_lengths)}")

        return transactions

    def get_frequent_items(self, top_n: int = 20) -> pd.Series:
        """Get the most frequent items in the dataset"""
        if self.data is None:
            print("No data loaded")
            return pd.Series()

        if 'itemDescription' not in self.data.columns:
            print("Error: 'itemDescription' column not found")
            return pd.Series()

        item_counts = self.data['itemDescription'].value_counts().head(top_n)
        return item_counts

    def clean_data(self) -> pd.DataFrame:
        """Clean the dataset by handling missing values and duplicates"""
        if self.data is None:
            print("No data loaded")
            return pd.DataFrame()

        # Remove duplicates
        initial_count = len(self.data)
        self.data = self.data.drop_duplicates()
        final_count = len(self.data)
        print(f"Removed {initial_count - final_count} duplicate rows")

        # Handle missing values in itemDescription
        if self.data['itemDescription'].isnull().sum() > 0:
            self.data = self.data.dropna(subset=['itemDescription'])
            print(f"Removed rows with missing item descriptions")

        return self.data