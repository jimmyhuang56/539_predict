# backtest/analyzer.py
import matplotlib.pyplot as plt
from collections import Counter

def analyze_backtest_results(hit_records, strategy_name="策略"):
    total_periods = len(hit_records)
    total_hits = sum(r["hits"] for r in hit_records)
    avg_hits = total_hits / total_periods if total_periods else 0
    hit_distribution = Counter(r["hits"] for r in hit_records)

    print(f"\n--- {strategy_name} 回測結果 ---")
    print(f"總期數：{total_periods}")
    print(f"總命中數：{total_hits}")
    print(f"平均每期命中：{avg_hits:.2f}")
    print("命中分布：")
    for hits in sorted(hit_distribution):
        print(f"命中 {hits} 號碼：{hit_distribution[hits]} 次")

    # 視覺化命中趨勢
    plt.figure(figsize=(12, 6))
    plt.plot([r["hits"] for r in hit_records], label="每期命中數", color='blue', marker='o')
    plt.xlabel("回測期數")
    plt.ylabel("命中號碼數")
    plt.title(f"{strategy_name} 策略命中趨勢")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()