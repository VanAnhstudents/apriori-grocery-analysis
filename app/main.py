import streamlit as st
import pandas as pd
import sys
import os
import matplotlib.pyplot as plt

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

    # Add debug mode
    debug_mode = st.sidebar.checkbox("Debug Mode", value=True)

    min_support = st.sidebar.slider("Minimum Support", 0.001, 0.1, 0.01, 0.001,
                                    help="Lower values will find more itemsets but may include rare combinations")
    min_confidence = st.sidebar.slider("Minimum Confidence", 0.1, 1.0, 0.5, 0.05,
                                       help="Lower values will generate more rules but they may be weaker")
    top_n_items = st.sidebar.slider("Top N Items for Visualization", 10, 50, 20)

    # Auto-recommend parameters button
    if st.sidebar.button("Auto-recommend Parameters"):
        min_support = 0.005
        min_confidence = 0.3
        st.sidebar.success("Recommended: Support=0.005, Confidence=0.3")

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

                if debug_mode:
                    st.subheader("🔍 Debug Information")
                    st.write(f"Total transactions prepared: {len(transactions)}")

                    if transactions:
                        st.write("First 5 transactions:")
                        for i, transaction in enumerate(transactions[:5]):
                            st.write(f"Transaction {i + 1}: {transaction}")

                if transactions:
                    # Analyze transaction patterns and recommend parameters
                    preprocessor.analyze_transaction_patterns()

                    # Visualizations
                    st.subheader("📈 Data Visualizations")

                    # Top items
                    item_counts = preprocessor.get_frequent_items(top_n_items)
                    if not item_counts.empty:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader(f"Top {top_n_items} Most Frequent Items")
                            fig1 = visualizer.plot_top_items(item_counts, top_n_items)
                            st.pyplot(fig1)
                            plt.close(fig1)  # Close the figure to free memory

                        with col2:
                            st.subheader(f"Top 10 Items Distribution")
                            fig2 = visualizer.plot_pie_chart_top_items(item_counts, 10)
                            st.pyplot(fig2)
                            plt.close(fig2)  # Close the figure to free memory

                    # Transaction length distribution
                    st.subheader("Transaction Length Distribution")
                    fig3 = visualizer.plot_transaction_length_distribution(transactions)
                    st.pyplot(fig3)
                    plt.close(fig3)  # Close the figure to free memory

                    # Run Apriori algorithm
                    if st.button("Run Apriori Algorithm"):
                        with st.spinner("Finding frequent itemsets and generating rules..."):
                            # Find frequent itemsets
                            frequent_itemsets = apriori_algo.find_frequent_itemsets(transactions)

                            if debug_mode:
                                st.subheader("🔍 Frequent Itemsets Debug")
                                if frequent_itemsets:
                                    total_itemsets = sum(len(itemsets) for itemsets in frequent_itemsets.values())
                                    st.write(f"Total frequent itemsets found: {total_itemsets}")

                                    for k, itemsets in frequent_itemsets.items():
                                        st.write(f"**{k}-itemsets:** {len(itemsets)}")
                                        if itemsets:
                                            st.write("First 10 itemsets:")
                                            for itemset, support in list(itemsets.items())[:10]:
                                                st.write(f"  {set(itemset)}: {support:.4f}")
                                else:
                                    st.warning("No frequent itemsets found!")
                                    st.info("Try lowering the minimum support threshold")

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

                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Frequent Itemsets", total_itemsets)
                                with col2:
                                    st.metric("Total Association Rules", len(rules))
                                with col3:
                                    if rules:
                                        st.metric("Highest Confidence", f"{rules[0]['confidence']:.4f}")
                                with col4:
                                    if rules:
                                        st.metric("Highest Lift", f"{max(r['lift'] for r in rules):.4f}")

                                # Itemset sizes
                                st.subheader("Frequent Itemsets by Size")
                                itemset_sizes = {k: len(v) for k, v in frequent_itemsets.items()}
                                sizes_df = pd.DataFrame({
                                    'Itemset Size': list(itemset_sizes.keys()),
                                    'Count': list(itemset_sizes.values())
                                })
                                st.bar_chart(sizes_df.set_index('Itemset Size'))

                                # Rules visualization
                                st.subheader("Rules Visualization")

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.subheader("Support vs Confidence")
                                    fig4 = visualizer.plot_rules_metrics(rules)
                                    if fig4:
                                        st.pyplot(fig4)
                                        plt.close(fig4)

                                with col2:
                                    st.subheader("Frequent Itemsets by Size")
                                    fig5 = visualizer.plot_itemset_sizes(frequent_itemsets)
                                    if fig5:
                                        st.pyplot(fig5)
                                        plt.close(fig5)

                                # Additional metrics visualization
                                st.subheader("Rule Metrics Overview")
                                fig6 = visualizer.plot_support_confidence_lift(rules, 15)
                                if fig6:
                                    st.pyplot(fig6)
                                    plt.close(fig6)

                                # Display top rules in an expandable section
                                with st.expander("View Top 10 Rules Details"):
                                    for i, rule in enumerate(rules[:10]):
                                        st.markdown(f"**Rule {i + 1}:**")
                                        st.write(
                                            f"**IF** {', '.join(rule['antecedent'])} **THEN** {', '.join(rule['consequent'])}")
                                        st.write(
                                            f"Support: {rule['support']:.4f}, Confidence: {rule['confidence']:.4f}, Lift: {rule['lift']:.4f}")
                                        st.write("---")

                            else:
                                st.error("No association rules found with the current parameters!")
                                st.subheader("🚨 Troubleshooting Guide")

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("""
                                    **Possible Causes:**
                                    - Minimum support too high
                                    - Minimum confidence too high  
                                    - Not enough multi-item transactions
                                    - Data needs cleaning
                                    """)

                                with col2:
                                    st.markdown("""
                                    **Solutions to Try:**
                                    1. Lower min support to 0.001-0.005
                                    2. Lower min confidence to 0.1-0.3
                                    3. Check if transactions have multiple items
                                    4. Enable debug mode for more info
                                    """)

                                # Quick fix buttons
                                st.subheader("Quick Parameter Adjustments")
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    if st.button("Try Lower Support (0.005)"):
                                        st.session_state.min_support = 0.005
                                        st.rerun()

                                with col2:
                                    if st.button("Try Lower Confidence (0.3)"):
                                        st.session_state.min_confidence = 0.3
                                        st.rerun()

                                with col3:
                                    if st.button("Try Both Low (0.005, 0.3)"):
                                        st.session_state.min_support = 0.005
                                        st.session_state.min_confidence = 0.3
                                        st.rerun()

                                if debug_mode and frequent_itemsets:
                                    st.info("""
                                    **Debug Info:** Frequent itemsets were found but no rules generated.
                                    This usually means the confidence threshold is too high, or the itemsets 
                                    don't have strong enough relationships to meet the confidence requirement.
                                    """)
                else:
                    st.error("Failed to prepare transactions from the dataset.")
                    st.info("""
                    **Check your data format:**
                    - Ensure there's an 'itemDescription' column
                    - For transaction grouping, include 'Member_number' and 'Date' columns
                    - Or include a 'Transaction' column for transaction IDs
                    """)

                    st.write("Available columns in your data:")
                    st.write(data.columns.tolist())


if __name__ == "__main__":
    main()