import random
import matplotlib.pyplot as plt

UNIT_COST = 63.1
TOTAL_COMBOS = 448
JACKPOT = 57000

def simulate_profit_on_day(n, unit_cost=UNIT_COST, total_combos=TOTAL_COMBOS, jackpot=JACKPOT):
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

def simulate_loss_if_no_win(days, unit_cost=UNIT_COST, total_combos=TOTAL_COMBOS):
    cumulative_cost = 0
    for day in range(1, days + 1):
        multiplier = day * 0.01
        daily_cost = round(unit_cost * total_combos * multiplier)
        cumulative_cost += daily_cost
    return cumulative_cost

def simulate_multiple_wins(win_days, unit_cost=UNIT_COST, total_combos=TOTAL_COMBOS, jackpot=JACKPOT):
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

def monte_carlo_simulation(win_rate=0.05, days=100, trials=1000, unit_cost=UNIT_COST, total_combos=TOTAL_COMBOS, jackpot=JACKPOT):
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
        "positive_rate": sum(1 for r in results if r > 0) / trials,
        "results": results
    }

def plot_profit_curve(max_day=50, unit_cost=63.1, total_combos=448, jackpot=57000):
    import matplotlib.pyplot as plt

    days = list(range(1, max_day + 1))
    profits = []
    for day in days:
        result = simulate_profit_on_day(day, unit_cost, total_combos, jackpot)
        profits.append(result["net_profit"])

    plt.figure(figsize=(10, 5))
    plt.plot(days, profits, marker='o', label="Net Profit")
    plt.axhline(0, color='gray', linestyle='--', label="Break-even Line")
    plt.title("Profit Curve for Single Win Strategy")
    plt.xlabel("Winning Day")
    plt.ylabel("Net Profit (NTD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def cli_strategy_simulator():
    print("\n🎯 歡迎使用策略模擬器")
    while True:
        print("\n請選擇模式：")
        print("1️⃣ 指定中獎日損益")
        print("2️⃣ 不中獎累積虧損")
        print("3️⃣ 多次中獎損益")
        print("4️⃣ Monte Carlo 模擬")
        print("5️⃣ 繪製損益曲線圖")
        print("0️⃣ 離開模擬器")
        mode = input("請輸入選項（0~5）：").strip()

        if mode == "0":
            print("👋 感謝使用，再見！")
            break

        elif mode == "1":
            day = int(input("請輸入中獎日：").strip())
            result = simulate_profit_on_day(day)
            print(f"\n📅 第 {day} 天中獎")
            print(f"💰 累積投注：{result['cumulative_cost']} 元")
            print(f"🎯 中獎金額：{result['reward']} 元")
            print(f"📊 淨利：{result['net_profit']} 元")

        elif mode == "2":
            days = int(input("請輸入不中獎天數：").strip())
            loss = simulate_loss_if_no_win(days)
            print(f"\n📉 {days} 天不中獎 → 累積虧損：{loss} 元")

        elif mode == "3":
            raw = input("請輸入中獎日（以逗號分隔）：").strip()
            win_days = list(map(int, raw.split(",")))
            result = simulate_multiple_wins(win_days)
            print(f"\n🎯 中獎日：{win_days}")
            print(f"💰 累積投注：{result['cumulative_cost']} 元")
            print(f"🎯 總中獎金額：{result['total_reward']} 元")
            print(f"📊 淨利：{result['net_profit']} 元")

        elif mode == "4":
            rate = float(input("請輸入命中率（例如 0.05）：").strip())
            days = int(input("模擬天數：").strip())
            trials = int(input("模擬次數：").strip())
            result = monte_carlo_simulation(win_rate=rate, days=days, trials=trials)
            print(f"\n🎲 Monte Carlo 模擬結果（{trials} 次）")
            print(f"📈 平均損益：{result['average_profit']:.2f} 元")
            print(f"📊 最大損益：{result['max_profit']} 元")
            print(f"📉 最小損益：{result['min_profit']} 元")
            print(f"✅ 獲利機率：{result['positive_rate']:.2%}")

        elif mode == "5":
            max_day = int(input("請輸入最大中獎日（例如 50）：").strip())
            plot_profit_curve(max_day=max_day)

        else:
            print("⚠️ 無效選項，請重新輸入")

if __name__ == "__main__":
    cli_strategy_simulator()