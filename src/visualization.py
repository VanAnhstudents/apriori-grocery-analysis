import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Dict
import numpy as np
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori as mlxtend_apriori
from mlxtend.frequent_patterns import association_rules as mlxtend_rules


class DataVisualizer:
    def __init__(self):
        plt.style.use('default')
        self.fig_size = (12, 8)
        sns.set_palette("husl")

    def plot_top_items(self, item_counts: pd.Series, top_n: int = 20, save_path: str = None):
        """Plot bar chart of top N most frequent items"""
        plt.figure(figsize=self.fig_size)
        top_items = item_counts.head(top_n)

        plt.barh(range(len(top_items)), top_items.values)
        plt.yticks(range(len(top_items)), top_items.index)
        plt.xlabel('Frequency')
        plt.ylabel('Items')
        plt.title(f'Top {top_n} Most Frequent Items')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_transaction_length_distribution(self, transactions: List[List[str]], save_path: str = None):
        """Plot distribution of transaction lengths"""
        transaction_lengths = [len(transaction) for transaction in transactions]

        plt.figure(figsize=self.fig_size)
        plt.hist(transaction_lengths, bins=30, edgecolor='black', alpha=0.7)
        plt.xlabel('Number of Items per Transaction')
        plt.ylabel('Frequency')
        plt.title('Distribution of Transaction Lengths')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

        print(f"Average items per transaction: {np.mean(transaction_lengths):.2f}")
        print(f"Max items per transaction: {max(transaction_lengths)}")
        print(f"Min items per transaction: {min(transaction_lengths)}")

    def plot_pie_chart_top_items(self, item_counts: pd.Series, top_n: int = 10, save_path: str = None):
        """Plot pie chart of top N items"""
        plt.figure(figsize=(10, 10))
        top_items = item_counts.head(top_n)

        plt.pie(top_items.values, labels=top_items.index, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title(f'Top {top_n} Items Distribution')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def create_heatmap_data(self, transactions: List[List[str]], top_items: int = 20) -> pd.DataFrame:
        """Create co-occurrence matrix for heatmap visualization"""
        # Use only top N items for better visualization
        all_items = [item for transaction in transactions for item in transaction]
        item_counts = pd.Series(all_items).value_counts()
        top_item_names = item_counts.head(top_items).index.tolist()

        # Filter transactions to include only top items
        filtered_transactions = []
        for transaction in transactions:
            filtered_trans = [item for item in transaction if item in top_item_names]
            if filtered_trans:
                filtered_transactions.append(filtered_trans)

        # Create binary matrix
        te = TransactionEncoder()
        te_ary = te.fit(filtered_transactions).transform(filtered_transactions)
        df = pd.DataFrame(te_ary, columns=te.columns_)

        # Calculate co-occurrence matrix
        cooccurrence_matrix = df.T.dot(df)
        np.fill_diagonal(cooccurrence_matrix.values, 0)  # Set diagonal to 0 for better visualization

        return cooccurrence_matrix

    def plot_heatmap(self, cooccurrence_matrix: pd.DataFrame, save_path: str = None):
        """Plot heatmap of item co-occurrences"""
        plt.figure(figsize=(15, 12))
        sns.heatmap(cooccurrence_matrix, annot=True, fmt='d', cmap='YlOrRd',
                    square=True, cbar_kws={'shrink': 0.8})
        plt.title('Item Co-occurrence Heatmap')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_rules_metrics(self, rules: List[Dict], save_path: str = None):
        """Plot scatter plot of support vs confidence for rules"""
        if not rules:
            print("No rules to visualize")
            return

        supports = [rule['support'] for rule in rules]
        confidences = [rule['confidence'] for rule in rules]
        lifts = [rule['lift'] for rule in rules]

        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(supports, confidences, c=lifts, cmap='viridis', alpha=0.6)
        plt.colorbar(scatter, label='Lift')
        plt.xlabel('Support')
        plt.ylabel('Confidence')
        plt.title('Association Rules: Support vs Confidence (colored by Lift)')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_itemset_sizes(self, frequent_itemsets: Dict, save_path: str = None):
        """Plot bar chart of frequent itemsets by size"""
        sizes = list(frequent_itemsets.keys())
        counts = [len(itemsets) for itemsets in frequent_itemsets.values()]

        plt.figure(figsize=(10, 6))
        plt.bar(sizes, counts, color='skyblue', edgecolor='black')
        plt.xlabel('Itemset Size')
        plt.ylabel('Number of Itemsets')
        plt.title('Frequent Itemsets by Size')

        for i, count in enumerate(counts):
            plt.text(sizes[i], count, str(count), ha='center', va='bottom')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()