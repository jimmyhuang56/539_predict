import streamlit as st
from pages_update_page import show_update_page
from pages_retrain_page import show_retrain_page
from pages_strategy_page import show_strategy_page
from pages_simulate_page import show_simulate_page
from pages_performance_page import show_performance_page
from pages_rl_simulation import show_rl_simulation_page
from pages_report_page import show_report_page
from pages_predict_page import show_predict_page 

st.set_page_config(page_title="選號策略 Dashboard", layout="wide")
st.sidebar.title("📂 功能選單")
page = st.sidebar.radio("請選擇頁面", [
    "📥 資料更新",
    "🧠 模型重訓",
    "🎯 策略選號",
    "💰 投注模擬",
    "📊 績效評估",
    "🧪 策略學習模擬(RL)",
    "🔮 頭尾預測選號",
    "📄 策略報告"  # 🆕 新頁籤
])


if page == "📥 資料更新":
    show_update_page()
elif page == "🧠 模型重訓":
    show_retrain_page()
elif page == "🎯 策略選號":
    show_strategy_page()
elif page == "💰 投注模擬":
    show_simulate_page()
elif page == "📊 績效評估":
    show_performance_page()
elif page == "🧪 策略學習模擬(RL)":
    show_rl_simulation_page()
elif page == "📄 策略報告":
    show_report_page()
elif page == "🔮 頭尾預測選號": 
    show_predict_page()


