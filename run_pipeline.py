import argparse
from modules_update_features import update_features
from modules_retrain_model import retrain_model
from modules_strategy_combiner import generate_strategy
from modules_betting_engine import simulate_betting
from modules_rl_simulation import run_rl_simulation
from modules_report_generator import generate_report
from datetime import datetime
from run_tail_model import run_tail_model
from run_head_model import run_head_model

def run_pipeline(mode="full"):
    if mode in ["full", "update"]:
        draw_date = input("請輸入期別（YYYY-MM-DD）：").strip()
        drawn_numbers = input("請輸入中獎號碼（以逗號分隔）：").strip()
        df = update_features(draw_date, drawn_numbers)
        print(f"📋 本期資料筆數：{len(df)}")

    if mode in ["full", "retrain"]:
        model, df_gain = retrain_model()
        print("✅ 主策略模型已重訓")
        print("📊 模型特徵重要性（前5）:")
        print(df_gain.head())

        print("🔮 頭尾預測模型也已同步重訓並儲存（tail_model.pkl / head_model.pkl）")

    if mode in ["full", "strategy"]:
        latest_df, df_sources, sets = generate_strategy()
        print(f"\n📋 本期資料筆數：{len(latest_df)}")

        print("\n🎯 綜合選號結果（多策略融合）：")
        for _, row in df_sources.iterrows():
            print(f"號碼 {row['number']:>2} ← 來自：{row['sources']}")

        print("\n📊 策略重疊統計：")
        for name, s in sets.items():
            print(f"{name:<8} → 選出 {len(s)} 個號碼")
        print(f"總綜合選號數：{len(df_sources)}")

    if mode in ["full", "simulate"]:
        result = simulate_betting()
        print("\n📈 投注模擬結果:")
        print(f"🔗 連碰 → {len(result['linked']['combos'])} 組，平均分數：{result['linked']['avg_score']:.4f}")
        print(f"🧱 柱碰 → {len(result['column']['combos'])} 組，平均分數：{result['column']['avg_score']:.4f}")

    if mode == "rl":
        print("🧪 開始執行策略學習模擬（RL）...")
        result = run_rl_simulation(num_select=6, num_episodes=1000)
        print("✅ 模擬完成！")
        print("🎯 最終偏好前10號碼：", result["top_numbers"])
        print("📈 最後10回合獎勵趨勢：", [round(r, 3) for r in result["reward_history"][-10:]])

    if mode == "report":
        draw_date = input("請輸入期別（YYYY-MM-DD）：").strip()
        drawn_numbers = input("請輸入中獎號碼（以逗號分隔）：").strip()
        save_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = generate_report(draw_date, drawn_numbers, save_path=save_path)

        print("\n📄 報告摘要：")
        print("📅 期別：", report.get("draw_date", "（未指定）"))
        print("🔢 中獎號碼：", report.get("drawn_numbers", "（未指定）"))
        print("策略來源：", report["strategy_sources"])
        print("融合選號前10：", [r["number"] for r in report["fusion_top10"]])
        print("RL 偏好前10：", report["rl_top10"])

        # 🧱 顯示最佳柱碰摘要
        best = report["best_column_combo"]
        print(f"\n🧱 最佳柱碰（{best['column_count']}柱）")
        print("🔢 使用號碼：", best["used_numbers"])
        for name, nums in best["columns"].items():
            print(f"  {name} → {nums}")
        print(f"🎯 組合總數：{best['total_combos']} 組")
        print(f"💰 總投注成本：NT${best['total_cost']}")
        print(f"📝 報告已儲存：{save_path}")
    if mode in ["full", "tail"]:
        print("🧠 執行尾數共振模型流程...")
        result = run_tail_model()
        print("\n📊 尾數預測結果：", result["predicted_tails"])
        print("🎯 選號結果：", result["selected_numbers"])
    if mode in ["full", "head"]:
        print("🧠 執行頭數共振模型流程...")
        result = run_head_model()
        print("\n📊 頭數預測結果：", result["predicted_heads"])
        print("🎯 選號結果：", result["selected_numbers"])



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "update", "retrain", "strategy", "simulate", "rl", "report", "head", "tail"], default="full")
    args = parser.parse_args()
    run_pipeline(mode=args.mode)