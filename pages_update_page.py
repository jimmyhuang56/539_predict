import streamlit as st
from modules_update_features import update_features
import pandas as pd

def show_update_page():
    st.title("📥 資料更新")
    with st.form("update_form"):
        draw_date = st.text_input("請輸入期別（YYYY-MM-DD）")
        drawn_numbers_str = st.text_input("請輸入中獎號碼（以逗號分隔）")
        submitted = st.form_submit_button("更新資料")

    if submitted:
        try:
            df_updated = update_features(draw_date, drawn_numbers_str)
            st.success(f"✅ 特徵資料已更新，共 {len(df_updated)} 筆號碼")
            st.dataframe(df_updated[df_updated["date"].astype(str) == draw_date])
        except Exception as e:
            st.error(f"❌ 更新失敗：{e}")