import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
st.markdown("""
<style>

.stApp {
    background-color: #FFFDF8;
}

h1 {
    color: #C1121F !important;
}

h2 {
    color: #1B4332 !important;
}

h3 {
    color: #C1121F !important;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
    border-left: 6px solid #C1121F;
}

div[data-testid="stExpander"] {
    border: 1px solid #D8E2DC;
    border-radius: 12px;
    background-color: #F7FBF8;
}

.stMultiSelect span[data-baseweb="tag"] {
    background-color: #C1121F !important;
}

div[data-baseweb="slider"] > div > div {
    background-color: #C1121F;
}

hr {
    border-color: #D8E2DC;
}

</style>
""", unsafe_allow_html=True)
st.set_page_config(
    page_title="Lebanon Food Inflation",
    page_icon="📊",
    layout="wide"
)
st.title("Lebanon's Food Inflation Crisis 🇱🇧")
st.write("An interactive exploration of food prices in Lebanon from 2001 to 2023.")
st.markdown("""
<div style="
    display: flex;
    gap: 20px;
    margin-top: 20px;
    margin-bottom: 30px;
">

<div style="
    flex: 1;
    background-color: #FFF0F0;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
">
    <div style="font-size: 35px;">🌲</div>
    <b>Lebanon</b>
</div>

<div style="
    flex: 1;
    background-color: #FFF7E6;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
">
    <div style="font-size: 35px;">🛒</div>
    <b>Food Prices</b>
</div>

<div style="
    flex: 1;
    background-color: #EAF7EE;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
">
    <div style="font-size: 35px;">💵</div>
    <b>Lebanese Pound</b>
</div>

<div style="
    flex: 1;
    background-color: #EEF4FF;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
">
    <div style="font-size: 35px;">📈</div>
    <b>2000–2023</b>
</div>

</div>
""", unsafe_allow_html=True)
st.subheader("Explore the Data")
st.write("Use the interactive controls to explore how food prices changed over time.")
food = pd.read_csv("food_cpi.csv")


food["Value"] = pd.to_numeric(food["Value"], errors="coerce")
food["Year"] = pd.to_numeric(food["Year"], errors="coerce")

food = food.dropna(subset=["Value", "Year"])

food["Year"] = food["Year"].astype(int)
st.header("Food Price Explorer")

min_year = int(food["Year"].min())
max_year = int(food["Year"].max())

year_range = st.slider(
    "Select a year range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

food_year_filtered = food[
    (food["Year"] >= year_range[0]) &
    (food["Year"] <= year_range[1]) &
    (food["Item"] == "Consumer Prices, Food Indices (2015 = 100)")
].copy()

month_order = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

available_months = [
    month for month in month_order
    if month in food_year_filtered["Month"].dropna().unique()
]

selected_months = st.multiselect(
    "Select month(s):",
    options=available_months,
    default=available_months
)

filtered_food = food_year_filtered[
    food_year_filtered["Month"].isin(selected_months)
].copy()

filtered_food = filtered_food.sort_values("StartDate")

fig = px.line(
    filtered_food,
    x="StartDate",
    y="Value",
    markers=True,
    title="How Have Food Prices Changed in Lebanon?",
    labels={
        "StartDate": "Date",
        "Value": "Food Price Index (2015 = 100)"
    }
)

fig.update_layout(
    hovermode="x unified"
)

st.plotly_chart(fig, width="stretch")

# VISUALIZATION 2 - EXCHANGE RATE

st.divider()
st.header("Food Prices & the Lebanese Pound")


exchange = pd.read_csv("exchange_rate.csv")


exchange["StartDate"] = pd.to_datetime(
    exchange["StartDate"],
    errors="coerce"
)

exchange["Value"] = pd.to_numeric(
    exchange["Value"],
    errors="coerce"
)

exchange = exchange.dropna(
    subset=["StartDate", "Value"]
)

exchange["Year"] = exchange["StartDate"].dt.year


exchange_filtered = exchange[
    (exchange["Year"] >= year_range[0]) &
    (exchange["Year"] <= year_range[1])
].copy()


exchange_filtered = exchange_filtered.sort_values("StartDate")

exchange_yearly = (
    exchange_filtered
    .groupby("Year", as_index=False)["Value"]
    .mean()
)

fig_exchange = px.line(
    exchange_yearly,
    x="Year",
    y="Value",
    markers=True,
    title="How Did the Lebanese Pound Change Over Time?",
    labels={
        "Year": "Year",
        "Value": "Exchange Rate (LBP per USD)"
    }
)

fig_exchange.update_layout(
    hovermode="x unified"
)

st.plotly_chart(fig_exchange, width="stretch")

st.divider()

st.header("Food Prices vs. the Lebanese Pound")

food_yearly = (
    food[
        (food["Item"] == "Consumer Prices, Food Indices (2015 = 100)") &
        (food["Year"] >= year_range[0]) &
        (food["Year"] <= year_range[1])
    ]
    .groupby("Year", as_index=False)["Value"]
    .mean()
)

comparison = food_yearly.merge(
    exchange_yearly,
    on="Year",
    suffixes=("_Food", "_Exchange")
)

comparison["Food Price Index (2000 = 100)"] = (
    comparison["Value_Food"] /
    comparison["Value_Food"].iloc[0] * 100
)

comparison["Exchange Rate Index (2000 = 100)"] = (
    comparison["Value_Exchange"] /
    comparison["Value_Exchange"].iloc[0] * 100
)

fig_comparison = px.line(
    comparison,
    x="Year",
    y=[
        "Food Price Index (2000 = 100)",
        "Exchange Rate Index (2000 = 100)"
    ],
    markers=True,
    title="Did Food Prices Rise Alongside the Lebanese Pound's Depreciation?"
)

fig_comparison.data[0].line.color = "blue"
fig_comparison.data[1].line.color = "green"

fig_comparison.update_layout(
    xaxis_title="Year",
    yaxis_title="Index (2000 = 100)",
    yaxis_type="log",
    legend_title="",
    hovermode="x unified"
)

st.plotly_chart(fig_comparison, width="stretch")

st.divider()

st.subheader("Key Insights")

st.info("""
**1. Food prices surged after 2020**

Food prices remained relatively stable for much of the earlier period, but increased dramatically after 2020, during Lebanon's economic and currency crisis.
""")

st.info("""
**2. The end of subsidies coincided with accelerating food prices**

Lebanon subsidized essential food imports during the crisis, but these subsidies were gradually reduced and phased out. The visualization shows that food prices accelerated sharply around this period, alongside the depreciation of the Lebanese pound.
""")
st.divider()

st.subheader("Design Justifications")

with st.expander("Why I Used a Year Range Slider"):
    st.write("""
    The year range slider allows users to explore how food prices changed during different periods and focus on specific stages of Lebanon's economic crisis. I chose a slider because time is continuous and ordered, making it more intuitive than selecting individual years from a dropdown. It also reduces visual clutter by allowing users to focus their attention on the period they are interested in.
    """)

with st.expander("Why I Used a Month Multiselect"):
    st.write("""
    The month multiselect allows users to compare food prices across specific months within their selected year range. I chose a multiselect because users may want to examine one month or compare several months at the same time. It is linked to the year-range selection, allowing users to progressively narrow the data and focus on the information most relevant to their question.
    """)