import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import ast

# Set page config
st.set_page_config(page_title="Shopper Spectrum", layout="wide")
st.title("🛍️ Shopper Spectrum")
st.caption("Customer Segmentation & Product Recommendation | EDA Dashboard")

# ---------- LOAD ALL DATA ----------
@st.cache_data
def load_data():
    # 1. LOAD RFM DATA AND FIX CUSTOMER ID
    rfm = pd.read_csv('rfm_data.csv', index_col=0)
    
    # 🔥 MAGIC FIX: Customer ID ko pakka Integer mein badlo (12347.0 -> 12347)
    # Pehle Float mein, phir Integer mein convert karo, taaki .0 hat jaaye
    rfm.index = rfm.index.astype(float).astype(int)
    
    # 2. LOAD RECOMMENDATION RULES
    rules = pd.read_csv('recommendation_rules.csv')
    rules['antecedents'] = rules['antecedents'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    rules['consequents'] = rules['consequents'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    
    # 3. LOAD CLEANED DATA FOR EDA
   df = pd.read_csv('cleaned_retail.zip', compression='zip')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], dayfirst=True)
    
    return rfm, rules, df

rfm, rules, df = load_data()

# Create three tabs
tab1, tab2, tab3 = st.tabs(["🔍 Product Recommender", "👤 Customer Segment", "📊 Business Insights"])

# ---------- TAB 1: Product Recommendation ----------
with tab1:
    st.header("Find Similar Products")
    
    all_products = set()
    for itemset in rules['antecedents']:
        for item in itemset:
            all_products.add(item)
    all_products = sorted(list(all_products))
    
    product_input = st.selectbox("Select or type a product:", all_products)
    
    if st.button("Recommend"):
        recommendations = rules[rules['antecedents'].apply(lambda x: product_input in x)]
        recommended = recommendations['consequents'].explode().unique()
        recommended = [item for item in recommended if item != product_input]
        
        if len(recommended) == 0:
            st.warning("⚠️ No recommendations found for this product.")
        else:
            st.success("✅ Top 5 Recommendations:")
            for i, prod in enumerate(recommended[:5], 1):
                st.write(f"{i}. {prod}")

# ---------- TAB 2: Customer Segmentation (ULTIMATE FIX) ----------
with tab2:
    st.header("Check Customer Segment")
    
    customer_id = st.number_input("Enter Customer ID (e.g., 12347):", min_value=0, step=1, format="%d")
    
    if st.button("Get Segment"):
        # Ab index pakka INTEGER hai, toh direct match ho jayega
        if customer_id in rfm.index:
            segment = rfm.loc[customer_id, 'Segment_Name']
            r_score = rfm.loc[customer_id, 'R_Score']
            f_score = rfm.loc[customer_id, 'F_Score']
            m_score = rfm.loc[customer_id, 'M_Score']
            
            st.success(f"✅ **Segment:** {segment}")
            st.metric("RFM Scores", f"{r_score}-{f_score}-{m_score}")
            
            if "Champion" in segment:
                st.balloons()
        else:
            # Agar nahi mila toh kuch sample IDs dikhao
            sample_ids = list(rfm.index[:5])
            st.error(f"❌ Customer ID not found. Try these valid IDs: {sample_ids}")

# ---------- TAB 3: Business Insights (EDA Charts) ----------
with tab3:
    st.header("📈 Exploratory Data Analysis (EDA)")
    st.caption("Here are the key insights from our dataset.")

    # Chart 1
    st.subheader("🏆 1. Top 10 Best-Selling Products")
    top_products = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    top_products.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_title('Top 10 Products by Quantity Sold')
    ax1.set_xlabel('Product')
    ax1.set_ylabel('Total Quantity')
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)

    # Chart 2
    st.subheader("🌍 2. Top 10 Countries by Revenue")
    country_sales = df.groupby('Country')['Revenue'].sum().sort_values(ascending=False).head(10)
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    country_sales.plot(kind='bar', ax=ax2, color='orange')
    ax2.set_title('Top 10 Countries by Revenue')
    ax2.set_xlabel('Country')
    ax2.set_ylabel('Total Revenue')
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)

    # Chart 3
    st.subheader("📅 3. Monthly Sales Trend")
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
    monthly_trend = df.groupby('YearMonth')['Revenue'].sum()
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    monthly_trend.plot(kind='line', marker='o', ax=ax3, color='green')
    ax3.set_title('Monthly Revenue Trend')
    ax3.set_xlabel('Month')
    ax3.set_ylabel('Total Revenue')
    ax3.grid(True, linestyle='--', alpha=0.6)
    ax3.tick_params(axis='x', rotation=45)
    st.pyplot(fig3)

    # Chart 4
    st.subheader("💰 4. Revenue Distribution per Invoice")
    invoice_revenue = df.groupby('InvoiceNo')['Revenue'].sum()
    fig4, ax4 = plt.subplots(figsize=(12, 5))
    ax4.hist(invoice_revenue, bins=50, color='purple', edgecolor='black', alpha=0.7)
    ax4.set_title('Distribution of Revenue per Invoice')
    ax4.set_xlabel('Revenue per Invoice')
    ax4.set_ylabel('Number of Invoices')
    ax4.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig4)

    # Chart 5
    st.subheader("🏃 5. Top 10 Most Active Customers")
    active_customers = df.groupby('CustomerID')['InvoiceNo'].nunique().sort_values(ascending=False).head(10)
    fig5, ax5 = plt.subplots(figsize=(10, 5))
    active_customers.plot(kind='bar', ax=ax5, color='red')
    ax5.set_title('Top 10 Customers by Order Frequency')
    ax5.set_xlabel('Customer ID')
    ax5.set_ylabel('Number of Orders')
    ax5.tick_params(axis='x', rotation=45)
    st.pyplot(fig5)

    st.success("✅ All charts loaded successfully!")