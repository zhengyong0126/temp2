import streamlit as st
from ml_price_predictor import predict_price

st.title("🏠 Malaysia Housing AI Assistant")

# --- Section 1: Housing Price Prediction ---
st.header("🔎 Estimate House Price")

location = st.selectbox("Location",
                        ["Subang Jaya", "Cheras", "Petaling Jaya", "Puchong", "Shah Alam", "Klang", "Mont Kiara",
                         "Cyberjaya", "Kajang", "Bangsar"])
prop_type = st.selectbox("Property Type", ["Condo", "Terrace", "Semi-D", "Apartment"])
built_up = st.number_input("Built-up Size (sqft)", value=900)
rooms = st.slider("Number of Rooms", 1, 6, 3)

if st.button("Predict Price"):
    price = predict_price(location, prop_type, built_up, rooms)
    st.success(f"Estimated Price: RM {price:,.2f}")

# --- Section 2: Affordability Checker ---
st.header("💰 Check Loan Affordability")

monthly_income = st.number_input("Your Monthly Income (RM)", min_value=1000, value=5000)
existing_debt = st.number_input("Existing Monthly Debt (RM)", min_value=0, value=500)
loan_tenure = st.slider("Loan Tenure (Years)", 5, 35, 30)
interest_rate = st.number_input("Interest Rate (% per year)", value=4.0)
down_payment = st.number_input("Available Down Payment (RM)", value=30000)

if st.button("Check Affordability"):
    # Assume 70% of income can go to debt (DSR = 0.7)
    max_monthly_commitment = monthly_income * 0.7 - existing_debt

    # Calculate max loan using reverse mortgage formula
    monthly_rate = (interest_rate / 100) / 12
    n_months = loan_tenure * 12

    if monthly_rate > 0:
        max_loan = max_monthly_commitment * ((1 + monthly_rate) ** n_months - 1) / (
                    monthly_rate * (1 + monthly_rate) ** n_months)
    else:
        max_loan = max_monthly_commitment * n_months

    max_house_price = max_loan + down_payment

    st.info(f"✅ Based on your income and DSR, you can afford a house up to **RM {max_house_price:,.2f}**.")
    st.caption("Note: This estimate assumes a max DSR of 70% and standard interest calculation.")

# Chat box
from chat_engine import ask_ai

st.header("💬 Ask the AI about Housing")

user_question = st.text_input("Type your question:")
if st.button("Ask AI"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        answer = ask_ai(user_question)
        st.success(answer)

# visualization
import pandas as pd
import plotly.express as px

st.header("📊 Explore Housing Trends")

df = pd.read_csv("housing_data.csv")

# --- Filters ---
st.subheader("🔍 Filter by:")
selected_locations = st.multiselect("Location", df["Location"].unique(), default=df["Location"].unique())
selected_types = st.multiselect("Property Type", df["Property_Type"].unique(), default=df["Property_Type"].unique())
min_price, max_price = st.slider("Price Range (RM)",
                                 int(df["Avg_Price"].min()),
                                 int(df["Avg_Price"].max()),
                                 (200000, 1000000), step=50000)

# --- Filter Logic ---
filtered = df[
    (df["Location"].isin(selected_locations)) &
    (df["Property_Type"].isin(selected_types)) &
    (df["Avg_Price"] >= min_price) &
    (df["Avg_Price"] <= max_price)
]

st.dataframe(filtered)

import io
from fpdf import FPDF

# CSV export
csv = filtered.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Download Filtered Data as CSV", data=csv, file_name="filtered_housing.csv", mime="text/csv")

# PDF export
def generate_pdf(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Filtered Housing Data", ln=True, align='C')

    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.2

    # Header
    for col in df.columns:
        pdf.cell(col_width, row_height, txt=str(col), border=1)
    pdf.ln(row_height)

    # Data rows
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, txt=str(item), border=1)
        pdf.ln(row_height)

    return pdf.output(dest='S').encode('latin-1')

pdf = generate_pdf(filtered)
st.download_button("⬇️ Download Filtered Data as PDF", data=pdf, file_name="filtered_housing.pdf", mime="application/pdf")



