"""Tiny demo UI. Run: streamlit run app.py"""
import pandas as pd
import streamlit as st

from categorizer import CONFIDENCE_THRESHOLD, categorize

st.title("Expense Categorizer (powered by Jev)")

tab1, tab2 = st.tabs(["Single transaction", "Upload CSV"])

with tab1:
    desc = st.text_input("Transaction description", "SWIGGY ORDER 4521")
    amount = st.number_input("Amount", min_value=0.0, value=450.0)
    if st.button("Categorize"):
        out = categorize(desc, amount)
        st.subheader(out["final_category"])
        st.write(f"Jev's top pick: **{out['category']}** (confidence {out['confidence']:.2f})")
        if out["final_category"] == "needs_review":
            st.warning(f"Confidence is below {CONFIDENCE_THRESHOLD}, so this is flagged for manual review.")
        st.bar_chart(pd.Series(out["probabilities"]))
        st.caption(f"Looks recurring: {out['recurring']:.0%}")

with tab2:
    f = st.file_uploader("CSV with a 'description' column (optional 'amount')", type="csv")
    if f:
        df = pd.read_csv(f)
        results = [categorize(r["description"], r.get("amount")) for _, r in df.iterrows()]
        df["category"] = [r["final_category"] for r in results]
        df["confidence"] = [round(r["confidence"], 2) for r in results]
        st.dataframe(df)
        if "amount" in df:
            st.bar_chart(df.groupby("category")["amount"].sum())
