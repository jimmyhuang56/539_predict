# db_loader.py
import sqlite3
from typing import List, Tuple

def get_latest_date(db_path: str) -> str:
    """
    查詢資料庫中最新的日期。
    :param db_path: SQLite 資料庫路徑
    :return: 最新日期字串，若無資料則回傳 None
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(date) FROM lotto_data")
        result = cursor.fetchone()
        return result[0] if result else None

def get_rows_by_date_range(db_path: str, start_date: str, end_date: str) -> List[Tuple[str, str]]:
    """
    根據日期區間查詢樂透資料。
    :param db_path: SQLite 資料庫路徑
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 結束日期 (YYYY-MM-DD)
    :return: List of (date, numbers_str)
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, numbers FROM lotto_data WHERE date BETWEEN ? AND ? ORDER BY date ASC",
            (start_date, end_date)
        )
        return cursor.fetchall()

def load_lotto_history(db_path: str, max_rows: int = 300) -> List[Tuple[str, str]]:
    """
    載入指定期數的樂透歷史資料。
    :param db_path: SQLite 資料庫路徑
    :param max_rows: 最多載入的期數
    :return: List of (date, numbers_str)
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, numbers FROM lotto_data ORDER BY date DESC LIMIT ?",
            (max_rows,)
        )
        rows = cursor.fetchall()
        return rows[::-1]  # 反轉成由舊到新