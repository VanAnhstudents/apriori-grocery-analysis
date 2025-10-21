import pandas as pd
import numpy as np
from typing import List, Dict, Any
import os
import json
from datetime import datetime


def save_results(frequent_itemsets: Dict, rules: List[Dict], output_path: str):
    """Save frequent itemsets and association rules to files"""

    # Create directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    # Save frequent itemsets
    itemset_data = []
    for k, itemsets in frequent_itemsets.items():
        for itemset, support in itemsets.items():
            itemset_data.append({
                'Itemset': ' & '.join(itemset),
                'Size': k,
                'Support': support
            })

    itemset_df = pd.DataFrame(itemset_data)
    itemset_df.to_csv(f"{output_path}/frequent_itemsets.csv", index=False)

    # Save association rules
    if rules:
        rules_data = []
        for rule in rules:
            rules_data.append({
                'antecedent': ' & '.join(rule['antecedent']),
                'consequent': ' & '.join(rule['consequent']),
                'support': rule['support'],
                'confidence': rule['confidence'],
                'lift': rule['lift'],
                'conviction': rule['conviction']
            })

        rules_df = pd.DataFrame(rules_data)
        rules_df.to_csv(f"{output_path}/association_rules.csv", index=False)

    # Save summary statistics
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_frequent_itemsets': sum(len(itemsets) for itemsets in frequent_itemsets.values()),
        'itemsets_by_size': {k: len(v) for k, v in frequent_itemsets.items()},
        'total_association_rules': len(rules),
        'min_support': None,  # These would need to be passed as parameters
        'min_confidence': None
    }

    with open(f"{output_path}/summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Results saved to {output_path}")


def print_summary(frequent_itemsets: Dict, rules: List[Dict]):
    """Print summary of results"""
    print("\n" + "=" * 60)
    print("APRIORI ALGORITHM RESULTS SUMMARY")
    print("=" * 60)

    total_itemsets = sum(len(itemsets) for itemsets in frequent_itemsets.values())
    print(f"Total frequent itemsets found: {total_itemsets}")

    for k, itemsets in frequent_itemsets.items():
        print(f"  {k}-itemsets: {len(itemsets)}")

    print(f"Total association rules found: {len(rules)}")

    if rules:
        print("\nTop 5 association rules (by confidence):")
        print("-" * 50)
        for i, rule in enumerate(rules[:5], 1):
            print(f"{i}. IF {rule['antecedent']} THEN {rule['consequent']}")
            print(f"   Support: {rule['support']:.4f}, Confidence: {rule['confidence']:.4f}, Lift: {rule['lift']:.4f}")
            print()

    print("=" * 60)


def validate_transactions(transactions: List[List[str]]) -> bool:
    """Validate that transactions are in correct format"""
    if not transactions:
        print("Error: No transactions provided")
        return False

    if not isinstance(transactions, list):
        print("Error: Transactions should be a list")
        return False

    for i, transaction in enumerate(transactions):
        if not isinstance(transaction, list):
            print(f"Error: Transaction {i} is not a list")
            return False

        for item in transaction:
            if not isinstance(item, str):
                print(f"Error: Non-string item found in transaction {i}")
                return False

    print(f"Validated {len(transactions)} transactions")
    return True


def calculate_metrics(transactions: List[List[str]], rules: List[Dict]) -> Dict[str, Any]:
    """Calculate additional metrics for the rule set"""
    if not rules:
        return {}

    total_transactions = len(transactions)

    # Calculate coverage (proportion of transactions covered by at least one rule)
    covered_transactions = set()
    for rule in rules:
        antecedent = rule['antecedent']
        for i, transaction in enumerate(transactions):
            if antecedent.issubset(set(transaction)):
                covered_transactions.add(i)

    coverage = len(covered_transactions) / total_transactions

    # Calculate average rule length
    avg_rule_length = np.mean([len(rule['antecedent']) + len(rule['consequent']) for rule in rules])

    metrics = {
        'coverage': coverage,
        'avg_rule_length': avg_rule_length,
        'total_transactions': total_transactions,
        'covered_transactions': len(covered_transactions)
    }

    return metrics


def export_rules_excel(rules: List[Dict], filename: str = "association_rules.xlsx"):
    """Export association rules to Excel file with formatting"""
    if not rules:
        print("No rules to export")
        return

    # Create DataFrame
    data = []
    for rule in rules:
        data.append({
            'Rule': f"IF {', '.join(rule['antecedent'])} THEN {', '.join(rule['consequent'])}",
            'Support': rule['support'],
            'Confidence': rule['confidence'],
            'Lift': rule['lift'],
            'Conviction': rule['conviction']
        })

    df = pd.DataFrame(data)

    # Create Excel writer and save
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Association Rules', index=False)

        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Association Rules']

        # Adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    print(f"Rules exported to {filename}")