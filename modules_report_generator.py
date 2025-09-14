import json
from datetime import datetime
from modules_update_features import update_features
from modules_retrain_model import retrain_model
from modules_strategy_combiner import generate_strategy
from modules_betting_engine import simulate_betting
from modules_rl_simulation import run_rl_simulation
from betting_strategy_engine import find_best_column_strategy, generate_betting_plan


def generate_report(draw_date=None, drawn_numbers=None, save_path="report.json"):
    report = {}
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report["timestamp"] = timestamp

    # 📅 資料更新（可選）
    if draw_date and drawn_numbers:
        df_updated = update_features(draw_date, drawn_numbers)
        report["draw_date"] = draw_date
        report["drawn_numbers"] = drawn_numbers
        report["updated_rows"] = len(df_updated)

    # 🧠 模型重訓
    model, df_gain = retrain_model()
    report["model_gain_top5"] = df_gain.head(5).to_dict(orient="records")

    # 🎯 策略選號
    latest_df, df_sources, sets = generate_strategy()
    fusion_top10 = latest_df.sort_values(by="fusion_score", ascending=False).head(10)
    report["fusion_top10"] = fusion_top10[["number", "fusion_score"]].to_dict(orient="records")
    report["strategy_sources"] = {k: len(v) for k, v in sets.items()}

    # 💰 投注模擬
    sim_result = simulate_betting()
    report["linked"] = {
        "count": len(sim_result["linked"]["combos"]),
        "avg_score": sim_result["linked"]["avg_score"],
        "total_cost": sim_result["linked"]["total_cost"]
    }
    report["column"] = {
        "count": len(sim_result["column"]["combos"]),
        "avg_score": sim_result["column"]["avg_score"],
        "total_cost": sim_result["column"]["total_cost"]
    }

    # 🧪 RL 模擬
    rl_result = run_rl_simulation()
    report["rl_top10"] = rl_result["top_numbers"]
    report["rl_reward_last10"] = [round(r, 3) for r in rl_result["reward_history"][-10:]]

    # 💾 儲存報告
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ 策略報告已儲存：{save_path}")
    return report