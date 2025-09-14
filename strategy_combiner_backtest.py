import pandas as pd
from xgboost import XGBClassifier

FEATURE_CSV = "features.csv"
TOP_N = 10
CONDITION_PARAMS = {
    "cooldown": 15,
    "momentum": -1,
    "score": 1.5
}

print("📦 載入特徵資料...")
df = pd.read_csv(FEATURE_CSV)
dates = sorted(df["date"].unique())


# 🧠 訓練模型一次即可
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
gain_dict = model.get_booster().get_score(importance_type='gain')

# 📈 回測每一期
hits = []
for date in dates:
    df_day = df[df["date"] == date].copy()

    # Top-N 分數
    df_day["score"] = (
        1.2 * df_day["is_hot_tail"] +
        1.0 * df_day["is_recent_hot"] +
        0.8 * df_day["momentum"] +
        0.6 * df_day["draw_streak"] +
        0.5 * df_day["freq_20"] +
        0.3 * df_day["tail_freq_10"] -
        0.2 * df_day["cooldown"]
    )
    topn = df_day.sort_values(by="score", ascending=False).head(TOP_N)

    # 條件選號
    condition = df_day[
        (df_day["is_hot_tail"] == 1) &
        (df_day["momentum"] >= CONDITION_PARAMS["momentum"]) &
        (df_day["cooldown"] < CONDITION_PARAMS["cooldown"]) &
        (df_day["score"] >= CONDITION_PARAMS["score"])
    ]

    # 模型機率選號
    X_day = df_day.drop(columns=["date", "number", "is_drawn", "score"])
    df_day["prob"] = model.predict_proba(X_day)[:, 1]
    model_prob = df_day.sort_values(by="prob", ascending=False).head(TOP_N)

    # 模型加權分數選號
    def compute_gain_score(row):
        return sum(gain_dict.get(f, 0) * row[f] for f in gain_dict if f in row)
    df_day["gain_score"] = df_day.apply(compute_gain_score, axis=1)
    gain = df_day.sort_values(by="gain_score", ascending=False).head(TOP_N)

    # 🔗 合併選號
    selected_nums = set()
    selected_nums.update(topn["number"])
    selected_nums.update(condition["number"])
    selected_nums.update(model_prob["number"])
    selected_nums.update(gain["number"])

    # 📊 命中統計
    hit_count = df_day[df_day["number"].isin(selected_nums)]["is_drawn"].sum()
    hits.append(hit_count)

# 🧾 統計結果
total = len(hits)
hit_rate = sum(1 for h in hits if h > 0) / total
avg_hits = sum(hits) / total
std_dev = pd.Series(hits).std()

print("\n📊 融合策略回測結果：")
print(f"總期數：{total}")
print(f"命中期數：{sum(1 for h in hits if h > 0)}")
print(f"命中率：{hit_rate:.2%}")
print(f"平均命中數：{avg_hits:.2f}")
print(f"命中穩定性（標準差）：{std_dev:.2f}")
