import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Customer Dashboard", layout="wide")

st.title("Customer Dashboard")


# Load Data

try:
    df_raw = pd.read_csv("messy_customer_data.csv")
    df_clean = pd.read_csv("cleaned_customer_data.csv")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()


# Sidebar Filters 

st.sidebar.title("Filters Panel")
st.sidebar.markdown("Use filters below to explore the data")

df_filtered = df_clean.copy()


# Country Filter

if "Country" in df_filtered.columns:
    st.sidebar.subheader("Country")

    country = st.sidebar.multiselect(
        "Select Country",
        options=sorted(df_filtered["Country"].dropna().unique()),
        default=sorted(df_filtered["Country"].dropna().unique())
    )

    df_filtered = df_filtered[df_filtered["Country"].isin(country)]


# Gender Filter

if "Gender" in df_filtered.columns:
    st.sidebar.subheader("Gender")

    gender = st.sidebar.multiselect(
        "Select Gender",
        options=sorted(df_filtered["Gender"].dropna().unique()),
        default=sorted(df_filtered["Gender"].dropna().unique())
    )

    df_filtered = df_filtered[df_filtered["Gender"].isin(gender)]

# Age Filter

if "Age" in df_filtered.columns:
    st.sidebar.subheader("Age Range")

    min_age = int(df_filtered["Age"].min())
    max_age = int(df_filtered["Age"].max())

    age_range = st.sidebar.slider(
        "Select Age Range",
        min_value=min_age,
        max_value=max_age,
        value=(min_age, max_age)
    )

    df_filtered = df_filtered[
        (df_filtered["Age"] >= age_range[0]) &
        (df_filtered["Age"] <= age_range[1])
    ]


# Purchase Filter

if "purchase_amount" in df_filtered.columns:
    st.sidebar.subheader("Purchase Amount")

    min_p = float(df_filtered["purchase_amount"].min())
    max_p = float(df_filtered["purchase_amount"].max())

    purchase_range = st.sidebar.slider(
        "Select Purchase Range",
        min_value=min_p,
        max_value=max_p,
        value=(min_p, max_p)
    )

    df_filtered = df_filtered[
        (df_filtered["purchase_amount"] >= purchase_range[0]) &
        (df_filtered["purchase_amount"] <= purchase_range[1])
    ]


# Info

st.sidebar.markdown("---")
st.sidebar.info("Filters update all charts automatically")


# Raw Data

st.header("Raw Data")
st.dataframe(df_raw.head(), width="stretch")
st.write("Dataset Shape:", df_raw.shape)


# Cleaned Data

st.header("Cleaned Data")
st.dataframe(df_clean.head(), width="stretch")
st.write("Shape After Cleaning:", df_clean.shape)


# KPIs

st.header("KPIs")

if "purchase_amount" in df_clean.columns:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Customers", df_clean.shape[0])

    with col2:
        st.metric("Total Revenue", round(df_clean["purchase_amount"].sum(), 2))

    with col3:
        st.metric("Average Purchase", round(df_clean["purchase_amount"].mean(), 2))
else:
    st.metric("Total Customers", df_clean.shape[0])


# Clean filtered data

if "purchase_amount" in df_filtered.columns:
    df_filtered = df_filtered.dropna(subset=["purchase_amount"])


# Charts

st.header("Charts")

# Customers by Country
if "Country" in df_filtered.columns:
    country_counts = df_filtered["Country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Count"]

    fig1 = px.bar(country_counts, x="Country", y="Count", title="Customers by Country")
    st.plotly_chart(fig1, width="stretch")

# Purchase Distribution
if "purchase_amount" in df_filtered.columns:
    fig2 = px.histogram(df_filtered, x="purchase_amount", nbins=30, title="Purchase Distribution")
    st.plotly_chart(fig2, width="stretch")

# Age vs Purchase
if "Age" in df_filtered.columns and "purchase_amount" in df_filtered.columns:
    fig3 = px.scatter(df_filtered, x="Age", y="purchase_amount", color="Gender", title="Age vs Purchase Amount")
    st.plotly_chart(fig3, width="stretch")

# Purchase by Gender
if "Gender" in df_filtered.columns and "purchase_amount" in df_filtered.columns:
    fig4 = px.box(df_filtered, x="Gender", y="purchase_amount", title="Purchase by Gender")
    st.plotly_chart(fig4, width="stretch")

# Monthly Trend
if "Signup_Date" in df_filtered.columns and "purchase_amount" in df_filtered.columns:

    df_filtered["Signup_Date"] = pd.to_datetime(df_filtered["Signup_Date"], errors="coerce")
    df_filtered["YearMonth"] = df_filtered["Signup_Date"].dt.to_period("M")

    monthly = df_filtered.groupby("YearMonth")["purchase_amount"].sum().reset_index()
    monthly["YearMonth"] = monthly["YearMonth"].astype(str)

    if not monthly.empty:
        fig5 = px.line(monthly, x="YearMonth", y="purchase_amount", title="Monthly Revenue Trend")
        st.plotly_chart(fig5, width="stretch")
