# betting_strategy_engine.py

import pandas as pd
from itertools import combinations, product
from typing import List, Tuple, Dict, Optional

TOP_N = 10
UNIT_COST = 50
FUSION_SCORE_COL = "fusion_score"

# 📦 載入處理後的選號資料（由 strategy_combiner.py 產出）
df = pd.read_csv("latest_processed_df.csv")

# 🔗 連碰組合生成器
def generate_linked_combinations(numbers: List[int], stars: int) -> List[Tuple[int]]:
    return list(combinations(numbers, stars))

# 🧱 柱碰組合生成器（支援任意柱數）
def generate_column_combinations(columns: List[List[int]], stars: int) -> List[Tuple[int]]:
    all_combos = []
    total_sets = len(list(combinations(columns, stars)))
    print(f"\n🧮 開始計算柱碰組合（stars={stars}, 柱數={len(columns)}）")
    print(f"🔄 共需處理 {total_sets} 組柱碰分法")

    for i, selected_columns in enumerate(combinations(columns, stars), start=1):
        raw = product(*selected_columns)
        valid = [combo for combo in raw if len(set(combo)) == stars]
        all_combos.extend(valid)
        print(f"✅ 處理第 {i}/{total_sets} 組柱碰 → 新增 {len(valid)} 組，目前累積 {len(all_combos)} 組")

    print(f"🎉 柱碰組合計算完成，共產生 {len(all_combos)} 組")
    return all_combos

# 💰 成本與統計計算器
def calculate_cost_and_stats(combos: List[Tuple[int]], unit_cost: int = UNIT_COST) -> Dict:
    total_cost = len(combos) * unit_cost
    return {
        "total_combos": len(combos),
        "total_cost": total_cost,
        "combos": combos
    }

# 📈 平均組合分數計算器
def compute_average_combo_score(df: pd.DataFrame, combos: List[Tuple[int]], score_col=FUSION_SCORE_COL) -> float:
    score_map = df.set_index("number")[score_col].to_dict()
    scores = [
        sum(score_map.get(num, 0) for num in combo) / len(combo)
        for combo in combos
    ]
    return sum(scores) / len(scores) if scores else 0

# 📊 每柱平均分數計算器
def compute_column_score(df: pd.DataFrame, columns: List[List[int]], score_col=FUSION_SCORE_COL) -> List[float]:
    score_map = df.set_index("number")[score_col].to_dict()
    return [
        sum(score_map.get(num, 0) for num in col) / len(col) if col else 0
        for col in columns
    ]

# 🧱 自動分柱（輪流分配）
def auto_split_columns(df: pd.DataFrame, score_col: str = FUSION_SCORE_COL, num_columns: int = 3) -> List[List[int]]:
    sorted_df = df.sort_values(by=score_col, ascending=False).reset_index(drop=True)
    columns = [[] for _ in range(num_columns)]
    for i, row in sorted_df.iterrows():
        col_index = i % num_columns
        columns[col_index].append(row["number"])
    return columns

# 🧠 主流程整合
def generate_betting_plan(
    selected_numbers: Optional[List[int]],
    stars: int,
    mode: str = "linked",
    columns: Optional[List[List[int]]] = None,
    unit_cost: int = UNIT_COST
) -> Dict:
    if mode == "linked":
        if not selected_numbers:
            raise ValueError("連碰模式需提供 selected_numbers")
        combos = generate_linked_combinations(selected_numbers, stars)

    elif mode == "column":
        if not columns or len(columns) < stars:
            raise ValueError("柱碰模式需提供足夠的 columns")
        combos = generate_column_combinations(columns, stars)

    else:
        raise ValueError("mode 必須為 'linked' 或 'column'")

    stats = calculate_cost_and_stats(combos, unit_cost)
    return stats

# 🧾 顯示投注結果
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
    avg_score = compute_average_combo_score(df, plan["combos"])
    print(f"📈 平均組合分數：{avg_score:.4f}")
    print("📋 前幾組預覽：")
    for combo in plan["combos"][:max_preview]:
        print("  組合 →", combo)

# 🧪 找出最佳分柱策略
def find_best_column_strategy(df: pd.DataFrame, max_columns: int = 6, stars: int = 3) -> Tuple[int, List[List[int]]]:
    best_score = -1
    best_columns = []
    best_column_count = 0

    print("\n🔍 分柱策略評估中...")
    for num_columns in range(3, max_columns + 1):
        columns = auto_split_columns(df, score_col=FUSION_SCORE_COL, num_columns=num_columns)
        combos = generate_column_combinations(columns, stars)
        avg_combo_score = compute_average_combo_score(df, combos)
        print(f"→ 分成 {num_columns} 柱：{len(combos)} 組，平均組合分數：{avg_combo_score:.4f}")

        if avg_combo_score > best_score:
            best_score = avg_combo_score
            best_columns = columns
            best_column_count = num_columns

    print(f"\n✅ 最佳分柱策略：{best_column_count} 柱，平均組合分數：{best_score:.4f}")
    return best_column_count, best_columns

# 🚀 主執行流程
if __name__ == "__main__":
    fusion_selected = df.sort_values(by=FUSION_SCORE_COL, ascending=False).head(TOP_N)
    selected_numbers = fusion_selected["number"].tolist()

    # 🔗 三星連碰
    plan_linked = generate_betting_plan(selected_numbers=selected_numbers, stars=3, mode="linked")
    display_betting_summary(plan_linked, title="🔗 三星連碰", source_numbers=selected_numbers)

    # 🧠 自動選出最佳柱數並分柱
    best_column_count, best_columns = find_best_column_strategy(fusion_selected, max_columns=6, stars=3)

    # 🧱 使用最佳分柱進行正式投注
    plan_best_column = generate_betting_plan(
        selected_numbers=None,
        stars=3,
        mode="column",
        columns=best_columns
    )

    flat_column_numbers = sorted(set(num for col in best_columns for num in col))
    title = f"🧱 最佳柱碰（{best_column_count}柱）"
    display_betting_summary(plan_best_column, title=title, source_numbers=flat_column_numbers, columns=best_columns)