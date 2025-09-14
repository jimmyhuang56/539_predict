import streamlit as st
from modules_betting_engine import simulate_betting

def show_simulate_page():
    st.title("💰 投注模擬")
    stars = st.slider("選擇投注星數", min_value=2, max_value=5, value=3)
    top_n = st.slider("選擇 Top-N 號碼數量", min_value=6, max_value=20, value=10)

    if st.button("開始模擬投注"):
        try:
            result = simulate_betting(stars=stars, top_n=top_n)

            st.subheader("🔗 三星連碰")
            st.write(f"號碼{result['linked']['numbers']}")
            st.write(f"組合數：{len(result['linked']['combos'])}")
            st.write(f"平均分數：{result['linked']['avg_score']:.4f}")
            st.write(f"總成本：NT${result['linked']['total_cost']}")
            for combo in result['linked']['combos'][:5]:
                st.write("→", combo)

            st.subheader("🧱 最佳柱碰")
            st.write(f"組合數：{len(result['column']['combos'])}")
            st.write(f"平均分數：{result['column']['avg_score']:.4f}")
            st.write(f"總成本：NT${result['column']['total_cost']}")
            for i, col in enumerate(result['column']['columns'], start=1):
                st.write(f"第 {i} 柱 →", sorted(col))
            for combo in result['column']['combos'][:5]:
                st.write("→", combo)
        except Exception as e:
            st.error(f"❌ 模擬失敗：{e}")