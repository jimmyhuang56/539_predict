#strategy_combiner.py
import pandas as pd
from xgboost import XGBClassifier

FEATURE_CSV = "features.csv"
TOP_N = 10
CONDITION_PARAMS = {
    "cooldown": 15,
    "momentum": -1,
    "score": 1.5
}

# 📦 載入資料
df = pd.read_csv(FEATURE_CSV)
latest_date = df["date"].max()
latest_df = df[df["date"] == latest_date].copy()

# 🧠 手動加權分數（Top-N）
latest_df["score"] = (
    1.2 * latest_df["is_hot_tail"] +
    1.0 * latest_df["is_recent_hot"] +
    0.8 * latest_df["momentum"] +
    0.6 * latest_df["draw_streak"] +
    0.5 * latest_df["freq_20"] +
    0.3 * latest_df["tail_freq_10"] -
    0.2 * latest_df["cooldown"]
)
topn_selected = latest_df.sort_values(by="score", ascending=False).head(TOP_N)

# 📊 條件選號
condition_selected = latest_df[
    (latest_df["is_hot_tail"] == 1) &
    (latest_df["momentum"] >= CONDITION_PARAMS["momentum"]) &
    (latest_df["cooldown"] < CONDITION_PARAMS["cooldown"]) &
    (latest_df["score"] >= CONDITION_PARAMS["score"])
]

# 🔮 模型預測機率選號
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
X_latest = latest_df.drop(columns=["date", "number", "is_drawn", "score"])
latest_df.loc[:, "prob"] = model.predict_proba(X_latest)[:, 1]
model_selected = latest_df.sort_values(by="prob", ascending=False).head(TOP_N)

# 📈 模型加權分數（gain_score）
gain_dict = model.get_booster().get_score(importance_type='gain')
def compute_gain_score(row):
    return sum(gain_dict.get(f, 0) * row[f] for f in gain_dict if f in row)
latest_df["gain_score"] = latest_df.apply(compute_gain_score, axis=1)
gain_selected = latest_df.sort_values(by="gain_score", ascending=False).head(TOP_N)
# 🔗 融合選號（融合分數）
latest_df["fusion_score"] = (
    0.4 * latest_df["score"] +
    0.3 * latest_df["prob"] +
    0.3 * latest_df["gain_score"]
)

fusion_selected = latest_df.sort_values(by="fusion_score", ascending=False).head(TOP_N)

#自動生成策略分數公式
def extract_gain_weights(model, normalize=True):
    gain_dict = model.get_booster().get_score(importance_type='gain')
    if normalize:
        total = sum(gain_dict.values())
        gain_dict = {k: v / total for k, v in gain_dict.items()}
    return gain_dict

def compute_strategy_score(df, weights, score_col="auto_score"):
    df[score_col] = df.apply(
        lambda row: sum(weights.get(f, 0) * row.get(f, 0) for f in weights),
        axis=1
    )
    return df

def generate_strategy_score(model, latest_df, normalize=True, score_col="auto_score"):
    weights = extract_gain_weights(model, normalize=normalize)
    latest_df = compute_strategy_score(latest_df, weights, score_col=score_col)
    return latest_df, weights

# 自動生成策略分數
latest_df, gain_weights = generate_strategy_score(model, latest_df)

# 融合模型機率與策略分數
latest_df["fusion_score"] = (
    0.5 * latest_df["auto_score"] +
    0.5 * latest_df["prob"]
)

# 精選 Top-N 號碼（依 fusion_score）
fusion_selected = latest_df.sort_values(by="fusion_score", ascending=False).head(TOP_N)

# 🔗 統整選號
def extract_numbers(df): return set(df["number"].tolist())
sets = {
    "Top-N": extract_numbers(topn_selected),
    "條件選號": extract_numbers(condition_selected),
    "模型機率": extract_numbers(model_selected),
    "模型加權": extract_numbers(gain_selected),
    "融合選號": extract_numbers(fusion_selected)

}

# 🧾 輸出綜合選號結果
print("\n🎯 綜合選號結果（多策略融合）：")
all_numbers = sorted(set.union(*sets.values()))
for num in all_numbers:
    sources = [name for name, s in sets.items() if num in s]
    print(f"號碼 {num:>2} ← 來自：{', '.join(sources)}")

# 📊 額外統計
print("\n📊 策略重疊統計：")
for name, s in sets.items():
    print(f"{name:<8} → 選出 {len(s)} 個號碼")
print(f"總綜合選號數：{len(all_numbers)}")

latest_df.to_csv("latest_processed_df.csv", index=False)