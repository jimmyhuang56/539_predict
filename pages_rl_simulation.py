import streamlit as st
import matplotlib.pyplot as plt
from modules_rl_simulation import run_rl_simulation

def show_rl_simulation_page():
    st.title("🧪 策略學習模擬（RL Prototype）")

    st.sidebar.subheader("🎛 模擬參數")
    num_select = st.sidebar.slider("每期選號數量", 3, 10, 6)
    num_episodes = st.sidebar.slider("訓練回合數", 100, 2000, 1000, step=100)
    reward_weights = {
        "命中率": st.sidebar.slider("命中率權重", 0.0, 1.0, 0.4),
        "報酬率": st.sidebar.slider("報酬率權重", 0.0, 1.0, 0.4),
        "重疊懲罰": st.sidebar.slider("重疊懲罰權重", 0.0, 1.0, 0.2)
    }

    if st.button("開始模擬訓練"):
        result = run_rl_simulation(
            num_select=num_select,
            num_episodes=num_episodes,
            reward_weights=reward_weights
        )

        st.success("✅ 模擬完成！")
        st.subheader("📈 獎勵演化趨勢")
        st.line_chart(result["reward_history"])

        st.subheader("📊 最終選號偏好分布（前20）")
        top_20 = result["preferences"][:20]
        fig, ax = plt.subplots()
        ax.bar([str(n) for n, _ in top_20], [p for _, p in top_20], color="orange")
        ax.set_ylabel("偏好值")
        ax.set_title("Top 20 號碼偏好分布")
        st.pyplot(fig)

        st.subheader("🎯 最終偏好前10號碼")
        st.write("→", result["top_numbers"])