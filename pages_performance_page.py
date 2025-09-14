import streamlit as st
from datetime import date

def show_performance_page():
    st.title("📊 績效評估")
    with st.form("performance_form"):
        draw_date = st.date_input("期別", value=date.today())
        invested = st.number_input("投入金額（NT$）", min_value=0)
        won = st.number_input("中獎金額（NT$）", min_value=0)
        notes = st.text_area("備註（可選）")
        submitted = st.form_submit_button("計算績效")

    if submitted:
        profit = won - invested
        roi = (won / invested - 1) * 100 if invested else 0
        is_profitable = profit > 0

        st.subheader("📈 本期績效結果")
        st.metric("💰 淨損益", f"NT${profit}")
        st.metric("📈 報酬率", f"{roi:.2f}%")
        st.success("✅ 本期獲利" if is_profitable else "❌ 本期虧損")

        performance_log = {
            "date": str(draw_date),
            "invested": invested,
            "won": won,
            "profit": profit,
            "roi": round(roi, 2),
            "is_profitable": is_profitable,
            "notes": notes
        }
        st.json(performance_log)