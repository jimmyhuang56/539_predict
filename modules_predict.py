# modules_predict.py
import os
import sqlite3
import numpy as np
import joblib
from datetime import datetime
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier

DB_PATH = "lotto_data.db"
TAIL_MODEL_PATH = "tail_model.pkl"
HEAD_MODEL_PATH = "head_model.pkl"

def load_draws():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT numbers FROM lotto_data ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()
    return [list(map(int, row[0].split(','))) for row in rows]

def build_matrix(draws, mode="tail"):
    if mode == "tail":
        return np.array([[1 if i in [n % 10 for n in draw] else 0 for i in range(10)] for draw in draws])
    elif mode == "head":
        return np.array([[1 if i in [n // 10 for n in draw] else 0 for i in range(4)] for draw in draws])
    else:
        raise ValueError("mode 必須是 'tail' 或 'head'")

def build_dataset(matrix, lookback=5):
    X, y = [], []
    for i in range(lookback, len(matrix)):
        X.append(matrix[i - lookback:i].flatten())
        y.append(matrix[i])
    return np.array(X), np.array(y).astype(int)

def predict_labels(matrix, model_path, lookback=5, threshold=0.5, n_labels=10):
    if not os.path.exists(model_path):
        X, y = build_dataset(matrix, lookback)
        model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
        model.fit(X, y)
        joblib.dump(model, model_path)
    else:
        model = joblib.load(model_path)

    latest = matrix[-lookback:].flatten().reshape(1, -1)
    probs = model.predict_proba(latest)
    return [i for i, prob in enumerate(probs) if prob[0][1] >= threshold]

def select_numbers(predicted_tails, predicted_heads, draws, top_n=6):
    candidates = [n for n in range(1, 40) if n % 10 in predicted_tails and n // 10 in predicted_heads]
    freq = Counter(n for draw in draws for n in draw)
    weighted_pool = [num for num in candidates for _ in range(freq[num] + 1)]
    selected = sorted(np.random.choice(list(set(weighted_pool)), size=min(top_n, len(set(weighted_pool))), replace=False))
    return selected

def predict_strategy(date_str=None, lookback=5, threshold=0.5, top_n=6):
    if date_str is None:
        date_str = datetime.today().strftime("%Y%m%d")

    draws = load_draws()
    tail_matrix = build_matrix(draws, mode="tail")
    head_matrix = build_matrix(draws, mode="head")

    predicted_tails = predict_labels(tail_matrix, TAIL_MODEL_PATH, lookback, threshold, n_labels=10)
    predicted_heads = predict_labels(head_matrix, HEAD_MODEL_PATH, lookback, threshold, n_labels=4)
    selected_numbers = select_numbers(predicted_tails, predicted_heads, draws, top_n)

    return {
        "date": date_str,
        "tails": predicted_tails,
        "heads": predicted_heads,
        "selected": selected_numbers
    }