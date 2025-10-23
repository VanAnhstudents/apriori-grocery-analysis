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
            print(f"Available columns: {self.data.columns.tolist()}")
            return []

        # Clean the item descriptions
        self.data['itemDescription'] = self.data['itemDescription'].str.strip().str.lower()

        # Group items by transaction
        transaction_column = None

        # Try to find transaction identifier
        if 'Member_number' in self.data.columns and 'Date' in self.data.columns:
            # Create transaction ID from Member_number and Date
            self.data['Transaction_ID'] = self.data['Member_number'].astype(str) + '_' + self.data['Date']
            transaction_column = 'Transaction_ID'
            print("Using Member_number + Date as transaction identifier")
        elif 'Transaction' in self.data.columns:
            transaction_column = 'Transaction'
            print("Using Transaction column as transaction identifier")
        else:
            # If no transaction ID, assume each row is a separate transaction
            print("Warning: No transaction identifier found. Using each row as a separate transaction.")
            transactions = [[item] for item in self.data['itemDescription'].values]
            self.transactions = transactions
            print(f"Created {len(transactions)} single-item transactions")
            return transactions

        # Group by transaction
        transactions = self.data.groupby(transaction_column)['itemDescription'].apply(list).tolist()

        # Filter out transactions with only one item (they can't generate rules)
        multi_item_transactions = [t for t in transactions if len(t) > 1]

        print(f"Original transactions: {len(transactions)}")
        print(f"Multi-item transactions (can generate rules): {len(multi_item_transactions)}")

        if len(multi_item_transactions) < len(transactions):
            print(f"Filtered out {len(transactions) - len(multi_item_transactions)} single-item transactions")

        self.transactions = multi_item_transactions

        # Print transaction statistics
        if self.transactions:
            transaction_lengths = [len(t) for t in self.transactions]
            print(f"Average items per transaction: {np.mean(transaction_lengths):.2f}")
            print(f"Max items per transaction: {max(transaction_lengths)}")
            print(f"Min items per transaction: {min(transaction_lengths)}")
            print(f"Sample transactions:")
            for i, transaction in enumerate(self.transactions[:3]):
                print(f"  Transaction {i + 1}: {transaction}")

        return self.transactions

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

        initial_count = len(self.data)

        # Remove duplicates
        self.data = self.data.drop_duplicates()
        after_dedup = len(self.data)
        print(f"Removed {initial_count - after_dedup} duplicate rows")

        # Handle missing values in itemDescription
        if self.data['itemDescription'].isnull().sum() > 0:
            before_null = len(self.data)
            self.data = self.data.dropna(subset=['itemDescription'])
            after_null = len(self.data)
            print(f"Removed {before_null - after_null} rows with missing item descriptions")

        # Clean item descriptions
        self.data['itemDescription'] = self.data['itemDescription'].str.strip().str.lower()

        return self.data

    def analyze_transaction_patterns(self):
        """Analyze transaction patterns for better parameter tuning"""
        if self.transactions is None:
            print("No transactions prepared")
            return

        transaction_lengths = [len(t) for t in self.transactions]

        print("\n=== Transaction Pattern Analysis ===")
        print(f"Total transactions: {len(self.transactions)}")
        print(f"Average items per transaction: {np.mean(transaction_lengths):.2f}")
        print(f"Standard deviation: {np.std(transaction_lengths):.2f}")
        print(f"Max items: {max(transaction_lengths)}")
        print(f"Min items: {min(transaction_lengths)}")

        # Recommend min_support based on data characteristics
        total_items = sum(transaction_lengths)
        avg_transaction_size = np.mean(transaction_lengths)

        # Simple heuristic for min_support
        recommended_support = max(0.001, 1 / (len(self.transactions) * 0.1))
        print(f"Recommended min_support: {recommended_support:.4f}")
        print(f"Recommended min_confidence: 0.3 - 0.5")