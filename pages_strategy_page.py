import streamlit as st
from modules_strategy_combiner import generate_strategy
from modules_betting_engine import simulate_betting

def show_strategy_page():
    st.title("🎯 策略選號")
    if st.button("產生策略選號"):
        try:
            latest_df, df_sources, sets = generate_strategy()
            st.success("✅ 策略選號完成！")
            st.dataframe(df_sources)

            st.subheader("📈 融合分數排序（前10）")
            st.dataframe(
                latest_df[["number", "fusion_score"]]
                .sort_values(by="fusion_score", ascending=False)
                .head(10)
            )

            st.subheader("📊 各策略選號數量")
            for name, s in sets.items():
                st.write(f"{name:<8} → 選出 {len(s)} 個號碼")
            st.write(f"🎯 綜合選號總數：{len(set.union(*sets.values()))}")
            
            # st.subheader("🔗 三星連碰組合預覽")
            # for combo in result["linked"]["combos"][:10]:
            #     st.write("→", "-".join(map(str, combo)))

            # st.subheader("🧱 柱碰分柱內容")
            # for i, col in enumerate(result["column"]["columns"], start=1):
            #     st.write(f"第 {i} 柱 →", sorted(col))

            # st.subheader("🧱 柱碰組合預覽")
            # for combo in result["column"]["combos"][:10]:
            #     st.write("→", "-".join(map(str, combo)))

        except Exception as e:
            st.error(f"❌ 策略選號失敗：{e}")