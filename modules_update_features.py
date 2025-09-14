#modules_update_features.py
import os
import pandas as pd
from ml_feature_generator import generate_features
from parser import parse_numbers_safely
from db_loader import load_lotto_history
import sqlite3

DB_PATH = "lotto_data.db"
FEATURE_CSV = "features.csv"

def standardize_date(date_str: str) -> str:
    return pd.to_datetime(date_str, errors="coerce").strftime("%Y-%m-%d")

def insert_draw_to_db(db_path: str, draw_date: str, drawn_numbers: set):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    numbers_str = ",".join(map(str, sorted(drawn_numbers)))
    draw_date_std = standardize_date(draw_date)

    cursor.execute("SELECT COUNT(*) FROM lotto_data WHERE date = ?", (draw_date_std,))
    if cursor.fetchone()[0] > 0:
        print(f"⚠️ 資料庫已包含 {draw_date_std}，將覆蓋該期資料")
        cursor.execute("DELETE FROM lotto_data WHERE date = ?", (draw_date_std,))

    cursor.execute("INSERT INTO lotto_data (date, numbers) VALUES (?, ?)", (draw_date_std, numbers_str))
    conn.commit()
    conn.close()
    print(f"✅ 已將 {draw_date_std} 的開獎號碼寫入資料庫：{numbers_str}")

def update_features(draw_date: str, drawn_numbers_str: str) -> pd.DataFrame:
    draw_date_std = pd.to_datetime(draw_date, errors="coerce").strftime("%Y-%m-%d")
    drawn_numbers = set(parse_numbers_safely(drawn_numbers_str))

    insert_draw_to_db(DB_PATH, draw_date_std, drawn_numbers)

    def is_feature_outdated(feature_csv_path: str, db_path: str) -> bool:
        if not os.path.exists(feature_csv_path):
            print("⚠️ 特徵表不存在，需重新產生")
            return True

        try:
            existing_df = pd.read_csv(feature_csv_path)
            latest_csv_date = pd.to_datetime(existing_df["date"].max(), errors="coerce")
        except Exception as e:
            print("⚠️ 無法讀取現有特徵表或日期欄位：", e)
            return True

        try:
            expected_df = generate_features(db_path, max_rows=100)
            latest_db_date = pd.to_datetime(expected_df["date"].max(), errors="coerce")
        except Exception as e:
            print("⚠️ 無法產生預期特徵表，請檢查 generate_features 或資料庫：", e)
            return True

        if latest_db_date > latest_csv_date:
            print(f"⚠️ 資料庫有更新（{latest_db_date} > {latest_csv_date}），需重新產生特徵表")
            return True

        REQUIRED_COLUMNS = [
            "draw_streak", "last_draw_gap", "cooldown", "momentum",
            "freq_10", "freq_20", "freq_30", "tail_digit", "zone",
            "tail_freq_10", "is_hot_tail", "streak_cooldown_combo", "is_recent_hot"
        ]
        missing_columns = set(REQUIRED_COLUMNS) - set(existing_df.columns)
        if missing_columns:
            print("⚠️ 特徵表缺少欄位：", missing_columns)
            return True

        return False

    if is_feature_outdated(FEATURE_CSV, DB_PATH):
        print("🔄 特徵表過期或資料庫有更新，重新產生中...")
        try:
            df_features = generate_features(DB_PATH, max_rows=5000)
            df_features["date"] = df_features["date"].astype(str)
            df_features.to_csv(FEATURE_CSV, index=False)
            print(f"✅ 特徵表已更新，共 {len(df_features)} 筆號碼")
        except Exception as e:
            print("❌ 特徵表更新失敗：", e)
            return pd.DataFrame()
    else:
        df_features = pd.read_csv(FEATURE_CSV)
        df_features["date"] = df_features["date"].astype(str)

        if draw_date_std in df_features["date"].values:
            print(f"⚠️ 特徵資料已包含期別 {draw_date_std}，將覆蓋該期標記")
            mask = df_features["date"] == draw_date_std
            df_features.loc[mask, "is_drawn"] = df_features.loc[mask, "number"].apply(
                lambda n: int(n in drawn_numbers)
            )
            try:
                df_features.to_csv(FEATURE_CSV, index=False)
                print(f"✅ 已更新特徵資料，共 {len(df_features)} 筆號碼")
            except Exception as e:
                print(f"❌ CSV 寫入失敗：{e}")
        else:
            print(f"⚠️ 特徵表中尚未包含期別 {draw_date_std}，請確認 generate_features 是否涵蓋該期")

    return df_features