# analyze_feature_importance.py
import pandas as pd
from xgboost import XGBClassifier

FEATURE_CSV = "features.csv"
TARGET_COLUMN = "is_drawn"

# 📦 載入特徵資料
print("📦 載入特徵資料...")
df = pd.read_csv(FEATURE_CSV)

# 🧪 切分特徵與標籤
X = df.drop(columns=["date", "number", TARGET_COLUMN])
y = df[TARGET_COLUMN]

# 🧠 訓練 XGBoost 模型
print("🧠 訓練 XGBoost 模型...")
model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=6,
    eval_metric="logloss",
    random_state=42
)
model.fit(X, y)

# 📊 顯示特徵重要性（Gain）
print("\n🎯 特徵重要性（依據資訊增益 gain）排序：")
importance = model.get_booster().get_score(importance_type='gain')
sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)

for rank, (feature, score) in enumerate(sorted_importance, start=1):
    print(f"{rank:>2}. {feature:<20} → gain: {score:.4f}")