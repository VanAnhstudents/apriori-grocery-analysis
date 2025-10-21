import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from apriori import Apriori


class TestApriori(unittest.TestCase):
    def setUp(self):
        self.apriori = Apriori(min_support=0.4, min_confidence=0.5)
        self.sample_transactions = [
            ['milk', 'bread'],
            ['milk', 'eggs'],
            ['bread', 'butter'],
            ['milk', 'bread', 'butter'],
            ['bread', 'eggs']
        ]

    def test_find_frequent_itemsets(self):
        frequent_itemsets = self.apriori.find_frequent_itemsets(self.sample_transactions)

        self.assertIsInstance(frequent_itemsets, dict)
        self.assertTrue(len(frequent_itemsets) > 0)

        # Check that all itemsets meet minimum support
        for k, itemsets in frequent_itemsets.items():
            for itemset, support in itemsets.items():
                self.assertGreaterEqual(support, self.apriori.min_support)

    def test_generate_rules(self):
        rules = self.apriori.generate_rules(self.sample_transactions)

        self.assertIsInstance(rules, list)

        if rules:
            # Check that all rules meet minimum confidence
            for rule in rules:
                self.assertGreaterEqual(rule['confidence'], self.apriori.min_confidence)

    def test_get_rules_dataframe(self):
        rules = self.apriori.generate_rules(self.sample_transactions)
        rules_df = self.apriori.get_rules_dataframe()

        self.assertIsInstance(rules_df, type(pd.DataFrame()))

        if not rules_df.empty:
            expected_columns = ['Antecedent', 'Consequent', 'Support', 'Confidence', 'Lift', 'Conviction']
            for col in expected_columns:
                self.assertIn(col, rules_df.columns)

    def test_empty_transactions(self):
        empty_transactions = []
        frequent_itemsets = self.apriori.find_frequent_itemsets(empty_transactions)

        self.assertEqual(frequent_itemsets, {})

    def test_single_item_transactions(self):
        single_transactions = [['milk'], ['bread'], ['milk']]
        frequent_itemsets = self.apriori.find_frequent_itemsets(single_transactions)

        self.assertIn(1, frequent_itemsets)
        self.assertGreater(len(frequent_itemsets[1]), 0)


if __name__ == '__main__':
    unittest.main()