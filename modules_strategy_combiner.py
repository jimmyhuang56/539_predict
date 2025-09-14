# modules_strategy_combiner.py

import pandas as pd
from xgboost import XGBClassifier

FEATURE_CSV = "features.csv"
TOP_N = 10
CONDITION_PARAMS = {
    "cooldown": 15,
    "momentum": -1,
    "score": 1.5
}

def generate_strategy(top_n: int = TOP_N):
    df = pd.read_csv(FEATURE_CSV)
    latest_date = df["date"].max()
    latest_df = df[df["date"] == latest_date].copy()

    # 🧠 手動加權分數
    latest_df["score"] = (
        1.2 * latest_df["is_hot_tail"] +
        1.0 * latest_df["is_recent_hot"] +
        0.8 * latest_df["momentum"] +
        0.6 * latest_df["draw_streak"] +
        0.5 * latest_df["freq_20"] +
        0.3 * latest_df["tail_freq_10"] -
        0.2 * latest_df["cooldown"]
    )
    topn_selected = latest_df.sort_values(by="score", ascending=False).head(top_n)

    # 📊 條件選號
    condition_selected = latest_df[
        (latest_df["is_hot_tail"] == 1) &
        (latest_df["momentum"] >= CONDITION_PARAMS["momentum"]) &
        (latest_df["cooldown"] < CONDITION_PARAMS["cooldown"]) &
        (latest_df["score"] >= CONDITION_PARAMS["score"])
    ]

    # 🔮 模型預測機率
    X = df.drop(columns=["date", "number", "is_drawn"])
    y = df["is_drawn"]
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=6,
        eval_metric="logloss",
        random_state=42
    )
    model.fit(X, y)
    X_latest = latest_df[X.columns]
    latest_df["prob"] = model.predict_proba(X_latest)[:, 1]
    model_selected = latest_df.sort_values(by="prob", ascending=False).head(top_n)

    # 📈 模型加權分數（gain_score）
    gain_dict = model.get_booster().get_score(importance_type='gain')
    latest_df["gain_score"] = latest_df.apply(
        lambda row: sum(gain_dict.get(f, 0) * row.get(f, 0) for f in gain_dict),
        axis=1
    )
    gain_selected = latest_df.sort_values(by="gain_score", ascending=False).head(top_n)

    # 🧠 自動策略分數（auto_score）
    total_gain = sum(gain_dict.values())
    gain_weights = {k: v / total_gain for k, v in gain_dict.items()}
    latest_df["auto_score"] = latest_df.apply(
        lambda row: sum(gain_weights.get(f, 0) * row.get(f, 0) for f in gain_weights),
        axis=1
    )

    # 🔗 融合分數
    latest_df["fusion_score"] = (
        0.5 * latest_df["auto_score"] +
        0.5 * latest_df["prob"]
    )
    fusion_selected = latest_df.sort_values(by="fusion_score", ascending=False).head(top_n)

    # 📋 建立選號來源對照表
    def extract_numbers(df): return set(df["number"].tolist())
    sets = {
        "Top-N": extract_numbers(topn_selected),
        "條件選號": extract_numbers(condition_selected),
        "模型機率": extract_numbers(model_selected),
        "模型加權": extract_numbers(gain_selected),
        "融合選號": extract_numbers(fusion_selected)
    }

    all_numbers = sorted(set.union(*sets.values()))
    source_map = []
    for num in all_numbers:
        sources = [name for name, s in sets.items() if num in s]
        source_map.append({"number": num, "sources": ", ".join(sources)})
    df_sources = pd.DataFrame(source_map)

    # 💾 儲存處理後資料
    latest_df.to_csv("latest_processed_df.csv", index=False)
    print(f"✅ 策略選號完成，共 {len(latest_df)} 筆號碼")

    return latest_df, df_sources, sets


# if __name__ == "__main__":
#     latest_df, df_sources, sets = generate_strategy()

#     print(f"\n📋 本期資料筆數：{len(latest_df)}")

#     print("\n🎯 綜合選號結果（多策略融合）：")
#     for _, row in df_sources.iterrows():
#         print(f"號碼 {row['number']:>2} ← 來自：{row['sources']}")

#     print("\n📊 策略重疊統計：")
#     for name, s in sets.items():
#         print(f"{name:<8} → 選出 {len(s)} 個號碼")
#     print(f"總綜合選號數：{len(df_sources)}")