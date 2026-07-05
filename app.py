import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import ast

st.set_page_config(page_title="Shopper Spectrum", layout="wide")
st.title("🛍️ Shopper Spectrum")
st.caption("Customer Segmentation & Product Recommendation | EDA Dashboard")

@st.cache_data
def load_data():
    rfm = pd.read_csv('rfm_data.csv', index_col=0)
    rfm.index = rfm.index.astype(float).astype(int)
    
    rules = pd.read_csv('recommendation_rules.csv')
    rules['antecedents'] = rules['antecedents'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    rules['consequents'] = rules['consequents'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    
    df = pd.read_csv('cleaned_retail.zip', compression='zip')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], dayfirst=True)
    
    return rfm, rules, df

rfm, rules, df = load_data()

tab1, tab2, tab3 = st.tabs(["🔍 Product Recommender", "👤 Customer Segment", "📊 Business Insights"])

with tab1:
    st.header("Find Similar Products")
    all_products = set()
    for itemset in rules['antecedents']:
        for item in itemset:
            all_products.add(item)
    all_products = sorted(list(all_products))
    product_input = st.selectbox("Select a product:", all_products)
    if st.button("Recommend"):
        recs = rules[rules['antecedents'].apply(lambda x: product_input in x)]
        recommended = recs['consequents'].explode().unique()
        recommended = [item for item in recommended if item != product_input]
        if len(recommended) == 0:
            st.warning("No recommendations found.")
        else:
            st.success("Top 5 Recommendations:")
            for i, prod in enumerate(recommended[:5], 1):
                st.write(f"{i}. {prod}")

with tab2:
    st.header("Check Customer Segment")
    customer_id = st.number_input("Enter Customer ID:", min_value=0, step=1, format="%d")
    if st.button("Get Segment"):
        if customer_id in rfm.index:
            segment = rfm.loc[customer_id, 'Segment_Name']
            st.success(f"✅ Segment: {segment}")
            if "Champion" in segment:
                st.balloons()
        else:
            sample_ids = list(rfm.index[:5])
            st.error(f"Try these valid IDs: {sample_ids}")

with tab3:
    st.header("📈 EDA Charts")
    # Chart 1
    st.subheader("1. Top 10 Products")
    top_products = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
    fig1, ax1 = plt.subplots(figsize=(10,5))
    top_products.plot(kind='bar', ax=ax1, color='skyblue')
    st.pyplot(fig1)

    # Chart 2
    st.subheader("2. Top 10 Countries")
    country_sales = df.groupby('Country')['Revenue'].sum().sort_values(ascending=False).head(10)
    fig2, ax2 = plt.subplots(figsize=(10,5))
    country_sales.plot(kind='bar', ax=ax2, color='orange')
    st.pyplot(fig2)

    # Chart 3
    st.subheader("3. Monthly Sales Trend")
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
    monthly_trend = df.groupby('YearMonth')['Revenue'].sum()
    fig3, ax3 = plt.subplots(figsize=(12,5))
    monthly_trend.plot(kind='line', marker='o', ax=ax3, color='green')
    st.pyplot(fig3)

    # Chart 4
    st.subheader("4. Revenue Distribution")
    invoice_revenue = df.groupby('InvoiceNo')['Revenue'].sum()
    fig4, ax4 = plt.subplots(figsize=(12,5))
    ax4.hist(invoice_revenue, bins=50, color='purple', edgecolor='black', alpha=0.7)
    st.pyplot(fig4)

    # Chart 5
    st.subheader("5. Most Active Customers")
    active = df.groupby('CustomerID')['InvoiceNo'].nunique().sort_values(ascending=False).head(10)
    fig5, ax5 = plt.subplots(figsize=(10,5))
    active.plot(kind='bar', ax=ax5, color='red')
    st.pyplot(fig5)

    st.success("✅ All charts loaded!")