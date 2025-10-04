import streamlit as st
import pandas as pd
from apyori import apriori

# Load the dataset
# IMPORTANT: Adjust the path to your CSV file
# For local execution, ensure 'WMT_Grocery_202209.csv' is in the same directory as app.py
try:
    store_data = pd.read_csv('WMT_Grocery_202209.csv')
except FileNotFoundError:
    st.error("Error: 'WMT_Grocery_202209.csv' not found. Please make sure the CSV file is in the same directory as the app.py file.")
    st.stop() # Stop the app if the file isn't found

# Prepare records for Apriori
records = []
for i in range(len(store_data)):
     records.append([str(store_data.values[i,j]) for j in range(0,4)])

# Run Apriori algorithm
@st.cache_data # Cache the results to avoid re-running on every interaction
def get_recommendations():
    association_rules = apriori(records, min_support=0.0030, min_confidence=0.2, min_lift=3, min_length=2)
    association_results = list(association_rules)
    return association_results

all_recommendations = get_recommendations()

# Function to format rules for display
def format_rule(item):
    pair = item[0]
    items = [x for x in pair]
    rule_str = f"If you buy **{items[0]}**, you might also like **{items[1]}**"
    return rule_str

# --- Streamlit Frontend ---
st.set_page_config(page_title="Grocery Recommendation System", layout="centered")

st.title("🛒 Grocery Recommendation System")

st.markdown("""
Welcome to the Grocery Recommendation System!
This system uses association rule mining (Apriori algorithm) to suggest items that are frequently bought together.
""")
st.info("The recommendations are based on a support of 0.003, confidence of 0.2, and lift of 3.")

# Display recommendations
if all_recommendations:
    st.header("Top Recommendations")

    # Let users filter by item
    all_items = sorted(list(set([item for sublist in records for item in sublist if item != 'nan'])))
    selected_item = st.selectbox("Select an item to see related recommendations (optional):", ["All Items"] + all_items)

    filtered_recommendations = []
    if selected_item == "All Items":
        filtered_recommendations = all_recommendations
    else:
        for rule in all_recommendations:
            pair = rule[0]
            if selected_item in pair:
                filtered_recommendations.append(rule)

    if filtered_recommendations:
        st.subheader(f"Recommendations for: {selected_item}")
        for i, item in enumerate(filtered_recommendations):
            rule_text = format_rule(item)
            support = item[1]
            confidence = item[2][0][2]
            lift = item[2][0][3]

            with st.expander(f"Recommendation {i+1}: {rule_text}"):
                st.write(f"**Rule:** {rule_text}")
                st.write(f"**Support:** {support:.4f} (Frequency of items appearing together)")
                st.write(f"**Confidence:** {confidence:.4f} (Probability that if item A is bought, item B is also bought)")
                st.write(f"**Lift:** {lift:.4f} (Increased likelihood of buying item B when item A is bought, compared to usual)")
                st.markdown("---")
    else:
        st.write(f"No specific recommendations found for '{selected_item}'. Try selecting 'All Items' or a different product.")

else:
    st.warning("No association rules found with the current parameters. Please check your data or adjust min_support, min_confidence, or min_lift.")

st.markdown("---")
st.markdown("Created with ❤️ using Streamlit")
