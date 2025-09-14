# pages_predict_page.py
import streamlit as st
from modules_predict import predict_strategy
import datetime
def show_predict_page():
    st.title("🔮 頭尾預測選號")

    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("📅 預測參考日期（系統將回溯前 N 期資料）", value=datetime.date.today())
        date_str = selected_date.strftime("%Y%m%d")

    with col2:
        top_n = st.slider("🎯 選號數量", min_value=1, max_value=10, value=6)

    lookback = st.slider("🔁 回溯期數", min_value=3, max_value=10, value=5)
    threshold = st.slider("📈 機率門檻", min_value=0.1, max_value=0.9, value=0.5)

    if st.button("開始預測"):
        result = predict_strategy(date_str=date_str or None, lookback=lookback, threshold=threshold, top_n=top_n)
        st.success(f"✅ 預測完成（期別：{result['date']}）")

        st.subheader("🎯 預測尾數")
        st.write(result["tails"])

        st.subheader("🎯 預測頭數")
        st.write(result["heads"])

        st.subheader("🎯 推薦號碼")
        st.write(result["selected"])