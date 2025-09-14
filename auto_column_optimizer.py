import pandas as pd
from itertools import combinations, product
from typing import List, Tuple, Dict, Optional
from collections import Counter

UNIT_COST = 50

def auto_split_columns_from_numbers(numbers: List[int], num_columns: int = 3) -> List[List[int]]:
    columns = [[] for _ in range(num_columns)]
    for i, num in enumerate(sorted(numbers)):
        col_index = i % num_columns
        columns[col_index].append(num)
    return columns

def generate_column_combinations(columns: List[List[int]], stars: int) -> List[Tuple[int]]:
    all_combos = set()
    for selected_columns in combinations(columns, stars):
        raw = product(*selected_columns)
        for combo in raw:
            if len(set(combo)) == stars:
                all_combos.add(tuple(sorted(combo)))  # 排序後加入 set 去重
    return sorted(all_combos)

def calculate_cost_and_stats(combos: List[Tuple[int]], unit_cost: int = UNIT_COST) -> Dict:
    total_cost = len(combos) * unit_cost
    return {
        "total_combos": len(combos),
        "total_cost": total_cost,
        "combos": combos
    }

def compute_average_combo_score(combos: List[Tuple[int]], score_map: Optional[Dict[int, float]] = None) -> float:
    if score_map:
        scores = [
            sum(score_map.get(num, 0) for num in combo) / len(combo)
            for combo in combos
        ]
    else:
        scores = [sum(combo) / len(combo) for combo in combos]
    return sum(scores) / len(scores) if scores else 0

def display_betting_summary(
    plan: Dict,
    title: str = "",
    max_preview: int = 5,
    source_numbers: Optional[List[int]] = None,
    columns: Optional[List[List[int]]] = None
):
    if title:
        print(f"\n📌 {title}")
    if source_numbers:
        print(f"🔢 使用號碼：{sorted(source_numbers)}")
    if columns:
        print(f"🧱 分柱內容（共 {len(columns)} 柱）：")
        for i, col in enumerate(columns, start=1):
            print(f"  第 {i} 柱 → {sorted(col)}")
    print(f"🎯 投注組合總數：{plan['total_combos']} 組")
    print(f"💰 總投注成本：NT${plan['total_cost']}")
    avg_score = compute_average_combo_score(plan["combos"])
    print(f"📈 平均組合分數：{avg_score:.4f}")
    print("📋 前幾組預覽：")
    for combo in plan["combos"][:max_preview]:
        print("  組合 →", combo)

def simulate_column_betting_with_custom_columns(
    input_numbers: List[int],
    stars: int = 3,
    num_columns: int = 3,
    unit_cost: int = UNIT_COST,
    score_map: Optional[Dict[int, float]] = None
) -> Dict:
    columns = auto_split_columns_from_numbers(input_numbers, num_columns=num_columns)
    combos = generate_column_combinations(columns, stars)
    plan = calculate_cost_and_stats(combos, unit_cost=unit_cost)

    flat_column_numbers = sorted(set(num for col in columns for num in col))
    title = f"🧱 自訂柱碰（{num_columns}柱）"
    display_betting_summary(plan, title=title, source_numbers=flat_column_numbers, columns=columns)

    return plan, columns, flat_column_numbers


def suggest_column_count(input_numbers: List[int], min_columns=3, max_columns=6) -> int:
    tail_counter = Counter(n % 10 for n in input_numbers)
    head_counter = Counter(n // 10 for n in input_numbers)

    tail_std = pd.Series(list(tail_counter.values())).std()
    head_std = pd.Series(list(head_counter.values())).std()

    score = (tail_std + head_std) / 2

    if score > 2.5:
        return max_columns
    elif score > 1.5:
        return max(min_columns + 1, max_columns - 1)
    else:
        return min_columns

def backtest_hit_rate(db_path: str, selected_numbers: set) -> None:
    import sqlite3
    from collections import Counter

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT date, numbers FROM lotto_data ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()

    hit_counts = []
    for date, numbers_str in rows:
        draw_numbers = set(map(int, numbers_str.split(",")))
        hits = selected_numbers & draw_numbers
        hit_counts.append(len(hits))

    total_periods = len(hit_counts)
    total_hits = sum(hit_counts)
    hit_distribution = Counter(hit_counts)

    print(f"\n📊 整體命中率回測（共 {total_periods} 期）")
    print(f"🎯 總命中次數：{total_hits}")
    print(f"📈 平均每期命中：{total_hits / total_periods:.2f}")
    print("📋 命中分布：")
    for k in sorted(hit_distribution):
        print(f"  命中 {k} 個 → {hit_distribution[k]} 期")

def simulate_column_hit_rate(db_path: str, columns: List[List[int]], stars: int = 3, preview_limit: int = 10) -> None:
    import sqlite3
    from collections import Counter

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT date, numbers FROM lotto_data ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()

    hit_distribution = Counter()
    hit_3_column_details = []

    for date, numbers_str in rows:
        draw_numbers = set(map(int, numbers_str.split(",")))
        hit_columns = sum(any(n in draw_numbers for n in col) for col in columns)
        hit_distribution[hit_columns] += 1

        if hit_columns == 3 and len(hit_3_column_details) < preview_limit:
            hit_3_column_details.append((date, sorted(draw_numbers)))

    total_periods = len(rows)
    hit_success = sum(v for k, v in hit_distribution.items() if k >= stars)

    print(f"\n🧪 柱碰命中率回測（{stars} 星）")
    print(f"✅ 命中期數（至少命中 {stars} 柱）：{hit_success} / {total_periods}")
    print(f"📈 命中率：{hit_success / total_periods:.2%}")
    print("📊 命中柱數分布：")
    for k in sorted(hit_distribution):
        print(f"  命中 {k} 柱 → {hit_distribution[k]} 期")

    if hit_3_column_details:
        print(f"\n🔍 命中 3 柱的期數（僅列出前 {preview_limit} 期）：")
        for date, nums in hit_3_column_details:
            print(f"  📅 {date} → 號碼：{nums}")
def list_latest_hit_3_columns(db_path: str, columns: List[List[int]], limit: int = 10) -> None:
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT date, numbers FROM lotto_data ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    hit_3_list = []
    for date, numbers_str in rows:
        draw_numbers = set(map(int, numbers_str.split(",")))
        hit_columns = sum(any(n in draw_numbers for n in col) for col in columns)
        if hit_columns == 3:
            hit_nums = sorted(draw_numbers & set(num for col in columns for num in col))
            hit_3_list.append((date, hit_nums, sorted(draw_numbers)))
            if len(hit_3_list) >= limit:
                break

    print(f"\n🔍 最新命中 3 柱的期數（共列出 {len(hit_3_list)} 期）：")
    for date, hit_nums, all_nums in hit_3_list:
        print(f"  📅 {date} → 命中號碼：{hit_nums}（原始號碼：{all_nums}）")

def analyze_hit_3_column_intervals(db_path: str, columns: List[List[int]]) -> None:
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT date, numbers FROM lotto_data ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()

    hit_indices = []
    for idx, (date, numbers_str) in enumerate(rows):
        draw_numbers = set(map(int, numbers_str.split(",")))
        hit_columns = sum(any(n in draw_numbers for n in col) for col in columns)
        if hit_columns == 3:
            hit_indices.append((idx, date))

    intervals = [j[0] - i[0] for i, j in zip(hit_indices[:-1], hit_indices[1:])]
    print(f"\n📊 命中 3 柱的期數間隔分析（共 {len(hit_indices)} 次命中）：")
    if intervals:
        print(f"📈 平均間隔期數：{sum(intervals) / len(intervals):.2f}")
        print("📋 間隔期數列表（最近幾次）：")
        for i, gap in enumerate(intervals[-10:], start=1):
            print(f"  第 {len(intervals) - 10 + i} 次 → 間隔 {gap} 期")
    else:
        print("⚠️ 尚未有足夠的命中資料計算間隔")

    print("\n📅 最近命中 3 柱的期數與間隔：")
    for i in range(1, len(hit_indices[-10:])):
        prev_idx, prev_date = hit_indices[-10 + i - 1]
        curr_idx, curr_date = hit_indices[-10 + i]
        gap = curr_idx - prev_idx
        print(f"  從 {prev_date} → {curr_date} 間隔 {gap} 期")

def find_profitable_win_day_for_column_bet(
    unit_cost: float = 63.1,
    total_combos: int = 448,
    jackpot: int = 57000,
    max_days: int = 1000
) -> Dict:
    cumulative_cost = 0
    for day in range(1, max_days + 1):
        multiplier = day * 0.01
        daily_cost = round(unit_cost * total_combos * multiplier)
        cumulative_cost += daily_cost
        reward = round(jackpot * multiplier)
        net_profit = reward - cumulative_cost
        if net_profit >= 0:
            return {
                "win_day": day,
                "multiplier": multiplier,
                "daily_cost": daily_cost,
                "cumulative_cost": cumulative_cost,
                "reward": reward,
                "net_profit": net_profit
            }
    return {
        "win_day": None,
        "cumulative_cost": cumulative_cost,
        "reward": 0,
        "net_profit": -cumulative_cost
    }

def find_min_win_day_to_break_even(unit_cost=63.1, total_combos=448, jackpot=57000, max_days=1000):
    cumulative_cost = 0
    for day in range(1, max_days + 1):
        multiplier = day * 0.01
        daily_cost = round(unit_cost * total_combos * multiplier)
        cumulative_cost += daily_cost
        reward = round(jackpot * multiplier)
        net_profit = reward - cumulative_cost
        if net_profit >= 0:
            return {
                "win_day": day,
                "multiplier": multiplier,
                "daily_cost": daily_cost,
                "cumulative_cost": cumulative_cost,
                "reward": reward,
                "net_profit": net_profit
            }
    return {
        "win_day": None,
        "cumulative_cost": cumulative_cost,
        "reward": 0,
        "net_profit": -cumulative_cost
    }

def simulate_profit_on_day(n, unit_cost=63.1, total_combos=448, jackpot=57000):
    cumulative_cost = 0
    for day in range(1, n + 1):
        multiplier = day * 0.01
        daily_cost = round(unit_cost * total_combos * multiplier)
        cumulative_cost += daily_cost
    reward = round(jackpot * (n * 0.01))
    net_profit = reward - cumulative_cost
    return {
        "day": n,
        "cumulative_cost": cumulative_cost,
        "reward": reward,
        "net_profit": net_profit
    }

def simulate_loss_if_no_win(days, unit_cost=63.1, total_combos=448):
    cumulative_cost = 0
    for day in range(1, days + 1):
        multiplier = day * 0.01
        daily_cost = round(unit_cost * total_combos * multiplier)
        cumulative_cost += daily_cost
    return cumulative_cost

def simulate_multiple_wins(win_days, unit_cost=63.1, total_combos=448, jackpot=57000):
    cumulative_cost = 0
    total_reward = 0
    for day in range(1, max(win_days) + 1):
        multiplier = day * 0.01
        daily_cost = round(unit_cost * total_combos * multiplier)
        cumulative_cost += daily_cost
        if day in win_days:
            total_reward += round(jackpot * multiplier)
    net_profit = total_reward - cumulative_cost
    return {
        "win_days": win_days,
        "cumulative_cost": cumulative_cost,
        "total_reward": total_reward,
        "net_profit": net_profit
    }

import random

def monte_carlo_simulation(win_rate=0.05, days=100, trials=1000, unit_cost=63.1, total_combos=448, jackpot=57000):
    results = []
    for _ in range(trials):
        cumulative_cost = 0
        total_reward = 0
        for day in range(1, days + 1):
            multiplier = day * 0.01
            daily_cost = round(unit_cost * total_combos * multiplier)
            cumulative_cost += daily_cost
            if random.random() < win_rate:
                total_reward += round(jackpot * multiplier)
        net_profit = total_reward - cumulative_cost
        results.append(net_profit)
    avg_profit = sum(results) / trials
    return {
        "trials": trials,
        "average_profit": avg_profit,
        "max_profit": max(results),
        "min_profit": min(results),
        "positive_rate": sum(1 for r in results if r > 0) / trials
    }



# 🚀 CLI 測試入口
if __name__ == "__main__":
    raw = input("請輸入號碼（以逗號分隔）：").strip()
    input_numbers = sorted(set(map(int, raw.split(","))))
    stars = int(input("請輸入每組選幾星（例如 3 或 4）：").strip())

    # 🧠 建議柱數
    suggested_columns = suggest_column_count(input_numbers)
    print(f"\n🧠 根據尾數與頭數分布，建議柱數為：{suggested_columns}")

    try:
        num_columns = int(input(f"請輸入柱數（預設 {suggested_columns}）：").strip())
    except:
        num_columns = suggested_columns

    # ❗ 防呆檢查：星數不能大於柱數
    if stars > num_columns:
        print(f"\n❌ 錯誤：你選擇了 {stars} 星，但只有 {num_columns} 柱，無法從不同柱中選出 {stars} 個號碼")
        print("✅ 請降低星數或增加柱數後再試一次")
        exit()

    # 📊 嘗試載入 fusion_score（可選）
    try:
        df = pd.read_csv("latest_processed_df.csv")
        score_map = df.set_index("number")["fusion_score"].to_dict()
    except:
        score_map = None

    plan, columns, flat_column_numbers = simulate_column_betting_with_custom_columns(
        input_numbers=input_numbers,
        stars=stars,
        num_columns=num_columns,
        score_map=score_map
    )
    
# 📊 回測整體命中率
backtest_hit_rate("lotto_data.db", set(flat_column_numbers))

# 🧪 回測柱碰命中率
simulate_column_hit_rate("lotto_data.db", columns, stars=stars)
list_latest_hit_3_columns("lotto_data.db", columns, limit=10)
analyze_hit_3_column_intervals("lotto_data.db", columns)
# # 根據實際組數計算總碰數
# total_combos = plan["total_combos"]

# # 套入損益模擬
# result = find_profitable_win_day_for_column_bet(total_combos=total_combos)

# if result["win_day"]:
#     print(f"\n📈 第 {result['win_day']} 天中獎可損益轉正")
#     print(f"💰 累積投注：{result['cumulative_cost']} 元")
#     print(f"🎯 中獎金額：{result['reward']} 元")
#     print(f"📊 淨利：{result['net_profit']} 元")
# else:
#     print("\n⚠️ 即使中獎也無法損益轉正（模擬範圍內）")
total_combos = plan["total_combos"]
result = find_min_win_day_to_break_even(total_combos=total_combos)

if result["win_day"]:
    print(f"\n📈 若一直未中，則需在第 {result['win_day']} 天中獎才能損益轉正")
    print(f"💰 累積投注：{result['cumulative_cost']} 元")
    print(f"🎯 中獎金額：{result['reward']} 元")
    print(f"📊 淨利：{result['net_profit']} 元")
else:
    print("\n⚠️ 即使中獎也無法損益轉正（模擬範圍內）")