import pandas as pd
from itertools import combinations, product
from typing import List, Tuple, Dict, Optional

FUSION_SCORE_COL = "fusion_score"
UNIT_COST = 50
TOP_N = 10

def generate_linked_combinations(numbers: List[int], stars: int) -> List[Tuple[int]]:
    return list(combinations(numbers, stars))

def auto_split_columns(df: pd.DataFrame, score_col: str = FUSION_SCORE_COL, num_columns: int = 3) -> List[List[int]]:
    sorted_df = df.sort_values(by=score_col, ascending=False).reset_index(drop=True)
    columns = [[] for _ in range(num_columns)]
    for i, row in sorted_df.iterrows():
        columns[i % num_columns].append(row["number"])
    return columns

def generate_column_combinations(columns: List[List[int]], stars: int) -> List[Tuple[int]]:
    all_combos = []
    for selected_columns in combinations(columns, stars):
        raw = product(*selected_columns)
        valid = [combo for combo in raw if len(set(combo)) == stars]
        all_combos.extend(valid)
    return all_combos

def compute_average_combo_score(df: pd.DataFrame, combos: List[Tuple[int]], score_col=FUSION_SCORE_COL) -> float:
    score_map = df.set_index("number")[score_col].to_dict()
    scores = [sum(score_map.get(num, 0) for num in combo) / len(combo) for combo in combos]
    return sum(scores) / len(scores) if scores else 0

def display_betting_summary(
    df: pd.DataFrame,
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
        for i, col in enumerate(columns, start=1):
            print(f"  第 {i} 柱 → {sorted(col)}")
    print(f"🎯 投注組合總數：{plan['total_combos']} 組")
    print(f"💰 總投注成本：NT${plan['total_cost']}")
    avg_score = compute_average_combo_score(df, plan["combos"])
    print(f"📈 平均組合分數：{avg_score:.4f}")
    print("📋 前幾組預覽：")
    for combo in plan["combos"][:max_preview]:
        print("  組合 →", combo)

def simulate_betting(stars: int = 3, top_n: int = TOP_N, unit_cost: int = UNIT_COST) -> Dict:
    df = pd.read_csv("latest_processed_df.csv")
    fusion_selected = df.sort_values(by=FUSION_SCORE_COL, ascending=False).head(top_n)
    selected_numbers = fusion_selected["number"].tolist()

    # 🔗 連碰
    linked_combos = generate_linked_combinations(selected_numbers, stars)
    linked_avg_score = compute_average_combo_score(df, linked_combos)
    linked_cost = len(linked_combos) * unit_cost

    plan_linked = {
        "total_combos": len(linked_combos),
        "total_cost": linked_cost,
        "combos": linked_combos
    }

    display_betting_summary(
        df,
        plan_linked,
        title="🔗 三星連碰",
        source_numbers=selected_numbers
    )

    # 🧱 柱碰（最佳柱數）
    best_score = -1
    best_columns = []
    best_combos = []
    for num_columns in range(3, 7):
        columns = auto_split_columns(fusion_selected, num_columns=num_columns)
        combos = generate_column_combinations(columns, stars)
        avg_score = compute_average_combo_score(df, combos)
        if avg_score > best_score:
            best_score = avg_score
            best_columns = columns
            best_combos = combos

    column_cost = len(best_combos) * unit_cost
    flat_column_numbers = sorted(set(num for col in best_columns for num in col))

    plan_column = {
        "total_combos": len(best_combos),
        "total_cost": column_cost,
        "combos": best_combos
    }

    title = f"🧱 最佳柱碰（{len(best_columns)}柱）"
    display_betting_summary(
        df,
        plan_column,
        title=title,
        source_numbers=flat_column_numbers,
        columns=best_columns
    )

    print(f"\n✅ 投注模擬完成：連碰 {len(linked_combos)} 組，柱碰 {len(best_combos)} 組")

    return {
        "linked": {
            "numbers": selected_numbers,
            "combos": linked_combos,
            "avg_score": linked_avg_score,
            "total_cost": linked_cost
        },
        "column": {
            "columns": best_columns,
            "combos": best_combos,
            "avg_score": best_score,
            "total_cost": column_cost
        }
    }