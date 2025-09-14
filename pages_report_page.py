import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

def show_report_page():
    st.title("📄 策略報告總覽")

    report_path = st.text_input("📁 輸入報告檔案路徑", value="report.json")

    if st.button("載入報告"):
        if not os.path.exists(report_path):
            st.error("❌ 找不到報告檔案")
            return

        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        st.success(f"✅ 成功載入報告（{report['timestamp']}）")

        # 📅 基本資訊
        st.subheader("📅 本期資料")
        st.write("期別：", report.get("draw_date", "未提供"))
        st.write("中獎號碼：", report.get("drawn_numbers", "未提供"))
        st.write("更新筆數：", report.get("updated_rows", "未提供"))

        # 🧠 模型摘要
        st.subheader("🧠 模型特徵重要性（Top 5）")
        st.dataframe(pd.DataFrame(report["model_gain_top5"]))

        # 🎯 策略選號摘要
        st.subheader("🎯 策略選號來源統計")
        st.write(report["strategy_sources"])

        st.subheader("📈 融合分數前10號碼")
        st.dataframe(pd.DataFrame(report["fusion_top10"]))

        # 💰 投注模擬結果
        st.subheader("💰 投注模擬結果")
        col1, col2 = st.columns(2)
        with col1:
            st.write("🔗 連碰")
            st.write(report["linked"])
        with col2:
            st.write("🧱 柱碰")
            st.write(report["column"])

        # 🧪 RL 模擬結果
        st.subheader("🧪 策略學習偏好（RL）")
        st.write("偏好前10號碼：", report["rl_top10"])
        st.line_chart(report["rl_reward_last10"])

        # 📦 原始 JSON 預覽
        with st.expander("📦 查看完整報告 JSON"):
            st.json(report)