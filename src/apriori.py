import pandas as pd
import numpy as np
from typing import List, Set, Tuple, Dict, Any
from itertools import combinations
from collections import defaultdict


class Apriori:
    def __init__(self, min_support: float = 0.01, min_confidence: float = 0.5):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequent_itemsets = {}
        self.association_rules = []

    def _get_frequent_1_itemsets(self, transactions: List[List[str]]) -> Dict[frozenset, float]:
        """Find frequent 1-itemsets"""
        item_counts = defaultdict(int)
        total_transactions = len(transactions)

        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1

        frequent_1_itemsets = {}
        for item, count in item_counts.items():
            support = count / total_transactions
            if support >= self.min_support:
                frequent_1_itemsets[frozenset([item])] = support

        print(f"Found {len(frequent_1_itemsets)} frequent 1-itemsets")
        return frequent_1_itemsets

    def _has_infrequent_subset(self, candidate: Set, prev_frequent: Dict) -> bool:
        """Check if any subset of candidate is infrequent"""
        k = len(candidate)
        if k <= 1:
            return False

        subsets = combinations(candidate, k - 1)

        for subset in subsets:
            if frozenset(subset) not in prev_frequent:
                return True
        return False

    def _apriori_gen(self, prev_frequent: Dict, k: int) -> Set[frozenset]:
        """Generate candidate itemsets of size k"""
        candidates = set()
        prev_itemsets = list(prev_frequent.keys())

        # Join step: combine itemsets that share first k-2 items
        for i in range(len(prev_itemsets)):
            for j in range(i + 1, len(prev_itemsets)):
                itemset1 = prev_itemsets[i]
                itemset2 = prev_itemsets[j]

                # Check if first k-2 items are the same
                if len(itemset1.union(itemset2)) == k:
                    new_candidate = itemset1.union(itemset2)

                    # Prune step: check if all subsets are frequent
                    if not self._has_infrequent_subset(new_candidate, prev_frequent):
                        candidates.add(new_candidate)

        return candidates

    def _calculate_support(self, itemset: Set, transactions: List[List[str]]) -> float:
        """Calculate support for an itemset"""
        count = 0
        for transaction in transactions:
            if itemset.issubset(set(transaction)):
                count += 1
        return count / len(transactions)

    def find_frequent_itemsets(self, transactions: List[List[str]]) -> Dict[int, Dict[frozenset, float]]:
        """Find all frequent itemsets using Apriori algorithm"""
        print("Finding frequent itemsets...")
        self.frequent_itemsets = {}

        # Find frequent 1-itemsets
        self.frequent_itemsets[1] = self._get_frequent_1_itemsets(transactions)
        k = 2

        while self.frequent_itemsets[k - 1]:
            print(f"Generating {k}-itemsets...")
            candidates = self._apriori_gen(self.frequent_itemsets[k - 1], k)
            frequent_k = {}

            for candidate in candidates:
                support = self._calculate_support(candidate, transactions)
                if support >= self.min_support:
                    frequent_k[candidate] = support

            self.frequent_itemsets[k] = frequent_k
            print(f"Found {len(frequent_k)} frequent {k}-itemsets")
            k += 1

        # Remove empty levels
        self.frequent_itemsets = {k: v for k, v in self.frequent_itemsets.items() if v}

        total_itemsets = sum(len(itemsets) for itemsets in self.frequent_itemsets.values())
        print(f"Total frequent itemsets found: {total_itemsets}")

        return self.frequent_itemsets

    def generate_rules(self, transactions: List[List[str]]) -> List[Dict[str, Any]]:
        """Generate association rules from frequent itemsets"""
        print("Generating association rules...")

        if not self.frequent_itemsets:
            self.find_frequent_itemsets(transactions)

        rules = []
        total_transactions = len(transactions)

        for k, itemsets in self.frequent_itemsets.items():
            if k < 2:  # Need at least 2 items to form a rule
                continue

            for itemset, support in itemsets.items():
                itemset_list = list(itemset)

                # Generate all possible rules
                for i in range(1, len(itemset_list)):
                    for antecedent in combinations(itemset_list, i):
                        antecedent = frozenset(antecedent)
                        consequent = itemset - antecedent

                        if not consequent:  # Skip if consequent is empty
                            continue

                        # Calculate confidence
                        antecedent_count = sum(1 for transaction in transactions
                                               if antecedent.issubset(set(transaction)))
                        if antecedent_count == 0:
                            continue

                        confidence = (support * total_transactions) / antecedent_count

                        if confidence >= self.min_confidence:
                            # Calculate lift
                            consequent_count = sum(1 for transaction in transactions
                                                   if consequent.issubset(set(transaction)))
                            consequent_support = consequent_count / total_transactions

                            if consequent_support > 0:
                                lift = confidence / consequent_support
                            else:
                                lift = float('inf')

                            # Calculate conviction
                            if confidence == 1:
                                conviction = float('inf')
                            else:
                                conviction = (1 - consequent_support) / (1 - confidence)

                            rules.append({
                                'antecedent': set(antecedent),
                                'consequent': set(consequent),
                                'support': support,
                                'confidence': confidence,
                                'lift': lift,
                                'conviction': conviction
                            })

        # Sort rules by confidence (descending)
        rules.sort(key=lambda x: x['confidence'], reverse=True)
        self.association_rules = rules

        print(f"Generated {len(rules)} association rules")
        return rules

    def get_rules_dataframe(self) -> pd.DataFrame:
        """Convert association rules to pandas DataFrame"""
        if not self.association_rules:
            return pd.DataFrame()

        data = []
        for rule in self.association_rules:
            data.append({
                'Antecedent': ' & '.join(rule['antecedent']),
                'Consequent': ' & '.join(rule['consequent']),
                'Support': f"{rule['support']:.4f}",
                'Confidence': f"{rule['confidence']:.4f}",
                'Lift': f"{rule['lift']:.4f}",
                'Conviction': f"{rule['conviction']:.4f}" if rule['conviction'] != float('inf') else 'inf'
            })

        return pd.DataFrame(data)

    def get_top_rules(self, n: int = 10, metric: str = 'confidence') -> List[Dict]:
        """Get top N rules based on specified metric"""
        if not self.association_rules:
            return []

        if metric not in ['support', 'confidence', 'lift', 'conviction']:
            metric = 'confidence'

        sorted_rules = sorted(self.association_rules, key=lambda x: x[metric], reverse=True)
        return sorted_rules[:n]