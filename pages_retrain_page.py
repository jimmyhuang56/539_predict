import streamlit as st
from modules_retrain_model import retrain_model
import matplotlib.pyplot as plt

def show_retrain_page():
    st.title("🧠 模型重訓")

    st.markdown("""
    本頁可選擇重訓以下模型：
    - 🎯 主策略模型（XGBoost）
    - 🔮 頭尾預測模型（RandomForest）
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        retrain_main = st.checkbox("重訓主模型", value=True)
    with col2:
        retrain_tail_head = st.checkbox("重訓頭尾模型", value=True)
    with col3:
        save_gain = st.checkbox("儲存特徵重要性", value=True)

    if st.button("開始重訓模型"):
        try:
            model, df_gain = retrain_model(
                save_model=retrain_main,
                save_gain=save_gain,
                save_tail_head=retrain_tail_head
            )
            st.success("✅ 模型重訓完成！")

            if retrain_main:
                st.subheader("📊 主模型特徵重要性（前10）")
                st.dataframe(df_gain)

                top_gain = df_gain.head(10)
                fig, ax = plt.subplots()
                ax.barh(top_gain["feature"], top_gain["gain"], color="skyblue")
                ax.invert_yaxis()
                ax.set_xlabel("Gain")
                ax.set_title("Top 10 特徵重要性")
                st.pyplot(fig)

            if retrain_tail_head:
                st.markdown("🔮 頭尾預測模型已重訓並儲存至 `models/tail_model.pkl` 與 `models/head_model.pkl`")

        except Exception as e:
            st.error(f"❌ 重訓失敗：{e}")