
import streamlit as st
import numpy_financial as npf
import pandas as pd

# App title
st.title("Enhanced Mortgage Amortization Calculator")

# Input fields for mortgage details
loan_amount = st.number_input("Loan Amount ($)", value=800000, step=1000.0)
interest_rate = st.number_input("Annual Interest Rate (%)", value=4.54, step=0.01)
amortization_years = st.number_input("Amortization Period (Years)", value=28, step=1)
term_years = st.number_input("Mortgage Term (Years)", value=3, step=1)
extra_payment = st.number_input("Extra Monthly Payment ($)", value=0.0, step=100.0)

if st.button("Generate Amortization Table"):
    # Convert inputs
    semi_annual_rate = (1 + (interest_rate / 200))**(1 / 6) - 1
    total_months = amortization_years * 12
    monthly_payment = npf.pmt(semi_annual_rate, total_months, -loan_amount)
    term_months = term_years * 12

    # Generate original amortization schedule
    schedule = []
    outstanding_balance = loan_amount
    total_interest_paid = 0

    for month in range(1, total_months + 1):
        interest_payment = outstanding_balance * semi_annual_rate
        principal_payment = monthly_payment - interest_payment
        extra_applied = 0

        if outstanding_balance > 0:
            # Add extra payment if applicable
            if extra_payment > 0:
                extra_applied = min(extra_payment, outstanding_balance - principal_payment)
            principal_payment += extra_applied
            outstanding_balance -= principal_payment

            total_interest_paid += interest_payment
            schedule.append([month, monthly_payment + extra_applied, principal_payment, interest_payment, max(outstanding_balance, 0)])

        # Stop if the mortgage is fully paid
        if outstanding_balance <= 0:
            break

    # Create DataFrame for updated schedule
    df = pd.DataFrame(schedule, columns=["Month", "Payment", "Principal", "Interest", "Remaining Balance"])
    df = df.round(2)  # Round values to 2 decimals

    # Calculate new amortization period and interest savings
    new_amortization_period = len(df)
    original_total_interest = npf.ipmt(semi_annual_rate, range(1, total_months + 1), total_months, -loan_amount).sum()
    interest_savings = original_total_interest - total_interest_paid

    # Display the updated table
    st.write("### Updated Amortization Schedule")
    st.dataframe(df.style.format("${:.2f}"))

    # Summary of savings and new amortization
    st.write("### Savings Summary")
    st.write(f"**New Amortization Period:** {new_amortization_period} months ({new_amortization_period // 12} years and {new_amortization_period % 12} months)")
    st.write(f"**Total Interest Savings:** ${interest_savings:,.2f}")

    # Provide an option to download the table
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Amortization Table as CSV",
        data=csv,
        file_name="updated_amortization_schedule.csv",
        mime="text/csv"
    )
