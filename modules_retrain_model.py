import os
import pandas as pd
import pickle
import joblib
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from datetime import datetime
from modules_predict import load_draws, build_matrix, build_dataset

FEATURE_CSV = "features.csv"
MODEL_DIR = "models"
TAIL_MODEL_PATH = os.path.join(MODEL_DIR, "tail_model.pkl")
HEAD_MODEL_PATH = os.path.join(MODEL_DIR, "head_model.pkl")

def retrain_model(save_model: bool = True, save_gain: bool = True, save_tail_head: bool = True):
    week_id = datetime.today().strftime("v%Yw%W")
    model_path = f"{MODEL_DIR}/model_{week_id}.pkl"
    gain_path = f"{MODEL_DIR}/gain_{week_id}.csv"
    os.makedirs(MODEL_DIR, exist_ok=True)

    # 🎯 主模型重訓（XGBoost）
    df = pd.read_csv(FEATURE_CSV)
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

    if save_model:
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        print(f"✅ 主模型已重訓並儲存：{model_path}")

    gain_dict = model.get_booster().get_score(importance_type='gain')
    df_gain = pd.DataFrame(gain_dict.items(), columns=["feature", "gain"]).sort_values(by="gain", ascending=False)

    if save_gain:
        df_gain.to_csv(gain_path, index=False)
        print(f"📊 特徵重要性已儲存：{gain_path}")

    # 🔮 頭尾模型重訓（RandomForest）
    if save_tail_head:
        draws = load_draws()
        lookback = 5

        # 尾數模型
        tail_matrix = build_matrix(draws, mode="tail")
        X_tail, y_tail = build_dataset(tail_matrix, lookback)
        tail_model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
        tail_model.fit(X_tail, y_tail)
        joblib.dump(tail_model, TAIL_MODEL_PATH)
        print(f"🔮 尾數模型已重訓並儲存：{TAIL_MODEL_PATH}")

        # 頭數模型
        head_matrix = build_matrix(draws, mode="head")
        X_head, y_head = build_dataset(head_matrix, lookback)
        head_model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
        head_model.fit(X_head, y_head)
        joblib.dump(head_model, HEAD_MODEL_PATH)
        print(f"🔮 頭數模型已重訓並儲存：{HEAD_MODEL_PATH}")

    return model, df_gain