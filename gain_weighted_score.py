import pandas as pd
from xgboost import XGBClassifier

FEATURE_CSV = "features.csv"
TARGET_COLUMN = "is_drawn"

# 📦 載入資料
df = pd.read_csv(FEATURE_CSV)
latest_date = df["date"].max()
latest_df = df[df["date"] == latest_date].copy()

# 🧪 準備訓練資料
X = df.drop(columns=["date", "number", TARGET_COLUMN])
y = df[TARGET_COLUMN]

# 🧠 訓練模型
model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=6,
    eval_metric="logloss",
    random_state=42
)
model.fit(X, y)

# 📊 取得 gain 作為加權係數
gain_dict = model.get_booster().get_score(importance_type='gain')

# 🔧 計算每個號碼的加權分數
def compute_score(row):
    score = 0
    for feature, gain in gain_dict.items():
        if feature in row:
            score += gain * row[feature]
    return score

latest_df["gain_score"] = latest_df.apply(compute_score, axis=1)

# 🔝 選出分數最高的前 N 個號碼
selected = latest_df.sort_values(by="gain_score", ascending=False).head(10)

# 📊 顯示結果
print("\n📈 模型加權分數選號結果（依 gain_score 排序）：")
for _, row in selected.iterrows():
    print(f"號碼 {row['number']:>2} → 分數 {row['gain_score']:.4f}")