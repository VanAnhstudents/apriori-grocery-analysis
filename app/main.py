import streamlit as st
import pandas as pd
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_preprocessing import DataPreprocessor
from visualization import DataVisualizer
from apriori import Apriori
from utils import save_results, print_summary


def main():
    st.set_page_config(
        page_title="Apriori Association Rule Mining",
        page_icon="🛒",
        layout="wide"
    )

    st.title("🛒 Apriori Association Rule Mining - Groceries Dataset")
    st.markdown("Discover interesting relationships between products using the Apriori algorithm")

    # Sidebar for parameters
    st.sidebar.header("Algorithm Parameters")
    min_support = st.sidebar.slider("Minimum Support", 0.001, 0.1, 0.01, 0.001)
    min_confidence = st.sidebar.slider("Minimum Confidence", 0.1, 1.0, 0.5, 0.05)
    top_n_items = st.sidebar.slider("Top N Items for Visualization", 10, 50, 20)

    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Initialize components
        preprocessor = DataPreprocessor()
        visualizer = DataVisualizer()
        apriori_algo = Apriori(min_support=min_support, min_confidence=min_confidence)

        # Load and explore data
        with st.spinner("Loading data..."):
            data = preprocessor.load_data(uploaded_file)

        if data is not None:
            # Display basic info
            st.subheader("📊 Dataset Overview")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Rows", data.shape[0])
            with col2:
                st.metric("Total Columns", data.shape[1])
            with col3:
                st.metric("Memory Usage", f"{data.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB")

            # Show data sample
            st.subheader("Data Sample")
            st.dataframe(data.head())

            # Data exploration
            if st.button("Explore Data"):
                with st.spinner("Analyzing data..."):
                    info = preprocessor.explore_data()

                    # Display missing values
                    st.subheader("Missing Values")
                    missing_df = pd.DataFrame({
                        'Column': info['missing_values'].index,
                        'Missing Count': info['missing_values'].values
                    })
                    st.dataframe(missing_df)

            # Prepare transactions
            with st.spinner("Preparing transactions..."):
                transactions = preprocessor.prepare_transactions()

                if transactions:
                    # Visualizations
                    st.subheader("📈 Data Visualizations")

                    # Top items
                    item_counts = preprocessor.get_frequent_items(top_n_items)
                    if not item_counts.empty:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader(f"Top {top_n_items} Most Frequent Items")
                            fig, ax = plt.subplots(figsize=(10, 8))
                            top_items = item_counts.head(top_n_items)
                            ax.barh(range(len(top_items)), top_items.values)
                            ax.set_yticks(range(len(top_items)))
                            ax.set_yticklabels(top_items.index)
                            ax.set_xlabel('Frequency')
                            ax.set_ylabel('Items')
                            st.pyplot(fig)

                        with col2:
                            st.subheader(f"Top 10 Items Distribution")
                            fig, ax = plt.subplots(figsize=(10, 8))
                            top_10 = item_counts.head(10)
                            ax.pie(top_10.values, labels=top_10.index, autopct='%1.1f%%', startangle=90)
                            ax.axis('equal')
                            st.pyplot(fig)

                    # Transaction length distribution
                    st.subheader("Transaction Length Distribution")
                    transaction_lengths = [len(transaction) for transaction in transactions]
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.hist(transaction_lengths, bins=30, edgecolor='black', alpha=0.7)
                    ax.set_xlabel('Number of Items per Transaction')
                    ax.set_ylabel('Frequency')
                    st.pyplot(fig)

                    # Run Apriori algorithm
                    if st.button("Run Apriori Algorithm"):
                        with st.spinner("Finding frequent itemsets and generating rules..."):
                            # Find frequent itemsets
                            frequent_itemsets = apriori_algo.find_frequent_itemsets(transactions)

                            # Generate association rules
                            rules = apriori_algo.generate_rules(transactions)

                            # Display results
                            st.subheader("🎯 Association Rules Results")

                            if rules:
                                # Convert to DataFrame for display
                                rules_df = apriori_algo.get_rules_dataframe()
                                st.dataframe(rules_df)

                                # Download results
                                csv = rules_df.to_csv(index=False)
                                st.download_button(
                                    label="Download Rules as CSV",
                                    data=csv,
                                    file_name="association_rules.csv",
                                    mime="text/csv"
                                )

                                # Summary statistics
                                st.subheader("Summary Statistics")
                                total_itemsets = sum(len(itemsets) for itemsets in frequent_itemsets.values())

                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Frequent Itemsets", total_itemsets)
                                with col2:
                                    st.metric("Total Association Rules", len(rules))
                                with col3:
                                    if rules:
                                        st.metric("Highest Confidence", f"{rules[0]['confidence']:.4f}")

                                # Itemset sizes
                                st.subheader("Frequent Itemsets by Size")
                                itemset_sizes = {k: len(v) for k, v in frequent_itemsets.items()}
                                sizes_df = pd.DataFrame({
                                    'Itemset Size': list(itemset_sizes.keys()),
                                    'Count': list(itemset_sizes.values())
                                })
                                st.bar_chart(sizes_df.set_index('Itemset Size'))

                            else:
                                st.warning(
                                    "No association rules found with the current parameters. Try lowering the minimum support or confidence.")
                else:
                    st.error("Failed to prepare transactions from the dataset.")


if __name__ == "__main__":
    main()