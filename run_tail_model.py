#run_tail_model.py
import os
import sqlite3
import csv
from datetime import datetime
from collections import Counter
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
import joblib

# ✅ 路徑初始化
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lotto_data.db")
LOG_PATH = os.path.join(BASE_DIR, "selection_log.csv")
MODEL_PATH = os.path.join(BASE_DIR, "tail_model.pkl")

# 🔍 環境檢查器
def check_environment():
    print("🔍 檢查執行環境...")
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"❌ 找不到資料庫：{DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT date, numbers FROM lotto_data LIMIT 1")
        conn.close()
        print("✅ 資料庫連線成功")
    except Exception as e:
        raise RuntimeError(f"❌ 資料庫結構錯誤：{e}")
    if not os.path.exists(LOG_PATH):
        print("📄 建立選號紀錄 CSV...")
        with open(LOG_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "predicted_tails", "selected_numbers"])
    else:
        print("✅ 選號紀錄 CSV 已存在")

# 📦 載入開獎資料
def load_draws():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT numbers FROM lotto_data ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()
    return [list(map(int, row[0].split(','))) for row in rows]

# 🧠 建立尾數矩陣
def build_tail_matrix(draws):
    tail_matrix = []
    for draw in draws:
        tails = [n % 10 for n in draw]
        row = [1 if i in tails else 0 for i in range(10)]
        tail_matrix.append(row)
    return np.array(tail_matrix)

# 🧠 建立訓練資料
def build_tail_dataset(tail_matrix, lookback=5):
    X, y = [], []
    for i in range(lookback, len(tail_matrix)):
        X.append(tail_matrix[i - lookback:i].flatten())
        y.append(tail_matrix[i])
    return np.array(X), np.array(y).astype(int)

# 🔮 預測下一期尾數
def predict_next_tail(model, tail_matrix, lookback=5, threshold=0.5):
    latest = tail_matrix[-lookback:].flatten().reshape(1, -1)
    probs = model.predict_proba(latest)
    predicted_tails = []
    for i, prob in enumerate(probs):
        if prob[0][1] >= threshold:
            predicted_tails.append(i)

    return predicted_tails


# 🎯 選號器（加權抽樣）
def select_numbers_from_tails(predicted_tails, history_draws, top_n=5):
    tail_to_numbers = {t: [n for n in range(1, 40) if n % 10 == t] for t in predicted_tails}
    candidate_numbers = [n for t in predicted_tails for n in tail_to_numbers[t]]
    freq_counter = Counter(n for draw in history_draws for n in draw)
    weighted_pool = []
    for num in candidate_numbers:
        weight = freq_counter[num] + 1
        weighted_pool.extend([num] * weight)
    selected = sorted(np.random.choice(list(set(weighted_pool)), size=min(top_n, len(set(weighted_pool))), replace=False))
    return selected

# 📂 儲存選號紀錄
def save_selection(tails, numbers):
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.today().strftime("%Y-%m-%d"),
            ",".join(map(str, tails)),
            ",".join(map(str, numbers))
        ])

# 🚀 主流程
def run_tail_model():
    check_environment()
    draws = load_draws()
    tail_matrix = build_tail_matrix(draws)
    X, y = build_tail_dataset(tail_matrix, lookback=5)

    print("🎯 訓練尾數共振模型...")
    model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)

    print("🔮 預測下一期尾數...")
    predicted_tails = predict_next_tail(model, tail_matrix, lookback=5, threshold=0.5)
    print("✅ 預測尾數：", predicted_tails)

    print("🎯 根據尾數共振挑出的號碼...")
    selected_numbers = select_numbers_from_tails(predicted_tails, draws, top_n=5)
    print("✅ 選號結果：", selected_numbers)

    print("📂 儲存選號紀錄...")
    save_selection(predicted_tails, selected_numbers)

    return {
        "predicted_tails": predicted_tails,
        "selected_numbers": selected_numbers
    }
