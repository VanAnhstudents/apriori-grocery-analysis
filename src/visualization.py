import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Dict
import numpy as np
from mlxtend.preprocessing import TransactionEncoder


class DataVisualizer:
    def __init__(self):
        plt.style.use('default')
        self.fig_size = (12, 8)
        sns.set_palette("husl")

    def plot_top_items(self, item_counts: pd.Series, top_n: int = 20):
        """Plot bar chart of top N most frequent items"""
        fig, ax = plt.subplots(figsize=self.fig_size)
        top_items = item_counts.head(top_n)

        ax.barh(range(len(top_items)), top_items.values)
        ax.set_yticks(range(len(top_items)))
        ax.set_yticklabels(top_items.index)
        ax.set_xlabel('Frequency')
        ax.set_ylabel('Items')
        ax.set_title(f'Top {top_n} Most Frequent Items')
        plt.tight_layout()

        return fig

    def plot_transaction_length_distribution(self, transactions: List[List[str]]):
        """Plot distribution of transaction lengths"""
        transaction_lengths = [len(transaction) for transaction in transactions]

        fig, ax = plt.subplots(figsize=self.fig_size)
        ax.hist(transaction_lengths, bins=30, edgecolor='black', alpha=0.7)
        ax.set_xlabel('Number of Items per Transaction')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Transaction Lengths')

        return fig

    def plot_pie_chart_top_items(self, item_counts: pd.Series, top_n: int = 10):
        """Plot pie chart of top N items"""
        fig, ax = plt.subplots(figsize=(10, 10))
        top_items = item_counts.head(top_n)

        ax.pie(top_items.values, labels=top_items.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title(f'Top {top_n} Items Distribution')

        return fig

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

    def plot_heatmap(self, cooccurrence_matrix: pd.DataFrame):
        """Plot heatmap of item co-occurrences"""
        fig, ax = plt.subplots(figsize=(15, 12))
        sns.heatmap(cooccurrence_matrix, annot=True, fmt='d', cmap='YlOrRd',
                    square=True, cbar_kws={'shrink': 0.8}, ax=ax)
        ax.set_title('Item Co-occurrence Heatmap')
        plt.tight_layout()

        return fig

    def plot_rules_metrics(self, rules: List[Dict]):
        """Plot scatter plot of support vs confidence for rules"""
        if not rules:
            print("No rules to visualize")
            return None

        supports = [rule['support'] for rule in rules]
        confidences = [rule['confidence'] for rule in rules]
        lifts = [rule['lift'] for rule in rules]

        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(supports, confidences, c=lifts, cmap='viridis', alpha=0.6)
        plt.colorbar(scatter, ax=ax, label='Lift')
        ax.set_xlabel('Support')
        ax.set_ylabel('Confidence')
        ax.set_title('Association Rules: Support vs Confidence (colored by Lift)')

        return fig

    def plot_itemset_sizes(self, frequent_itemsets: Dict):
        """Plot bar chart of frequent itemsets by size"""
        sizes = list(frequent_itemsets.keys())
        counts = [len(itemsets) for itemsets in frequent_itemsets.values()]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(sizes, counts, color='skyblue', edgecolor='black')
        ax.set_xlabel('Itemset Size')
        ax.set_ylabel('Number of Itemsets')
        ax.set_title('Frequent Itemsets by Size')

        for i, count in enumerate(counts):
            ax.text(sizes[i], count, str(count), ha='center', va='bottom')

        return fig

    def plot_support_confidence_lift(self, rules: List[Dict], top_n: int = 20):
        """Plot support, confidence and lift for top N rules"""
        if not rules:
            return None

        top_rules = rules[:top_n]

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

        # Support
        supports = [rule['support'] for rule in top_rules]
        ax1.bar(range(len(supports)), supports, color='lightblue')
        ax1.set_xlabel('Rule Index')
        ax1.set_ylabel('Support')
        ax1.set_title('Support for Top Rules')
        ax1.tick_params(axis='x', rotation=45)

        # Confidence
        confidences = [rule['confidence'] for rule in top_rules]
        ax2.bar(range(len(confidences)), confidences, color='lightgreen')
        ax2.set_xlabel('Rule Index')
        ax2.set_ylabel('Confidence')
        ax2.set_title('Confidence for Top Rules')
        ax2.tick_params(axis='x', rotation=45)

        # Lift
        lifts = [rule['lift'] for rule in top_rules]
        ax3.bar(range(len(lifts)), lifts, color='lightcoral')
        ax3.set_xlabel('Rule Index')
        ax3.set_ylabel('Lift')
        ax3.set_title('Lift for Top Rules')
        ax3.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        return fig