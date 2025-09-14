import numpy as np
import random

def run_rl_simulation(num_select=5, num_episodes=1000, reward_weights=None):
    if reward_weights is None:
        reward_weights = {"命中率": 0.4, "報酬率": 0.4, "重疊懲罰": 0.2}

    NUMBERS = list(range(1, 40))
    preferences = np.ones(len(NUMBERS)) / len(NUMBERS)
    reward_history = []
    prev_selection = []

    def simulate_draw():
        return set(random.sample(NUMBERS, num_select))

    def evaluate(selection, draw):
        hits = len(set(selection) & draw)
        invested = 300
        won = hits * 500
        roi = (won - invested) / invested
        return hits, roi

    def compute_reward(hits, roi, selection, prev_selection):
        overlap = len(set(selection) & set(prev_selection)) / num_select if len(prev_selection) > 0 else 0
        reward = (
            reward_weights["命中率"] * (hits / num_select) +
            reward_weights["報酬率"] * roi -
            reward_weights["重疊懲罰"] * overlap
        )
        return reward

    def update_preferences(preferences, selection, reward, lr=0.01):
        for num in selection:
            idx = NUMBERS.index(num)
            preferences[idx] += lr * reward
        preferences = np.clip(preferences, 0.01, None)
        preferences /= preferences.sum()
        return preferences

    for ep in range(num_episodes):
        selection = np.random.choice(NUMBERS, num_select, p=preferences, replace=False)
        draw = simulate_draw()
        hits, roi = evaluate(selection, draw)
        reward = compute_reward(hits, roi, selection, prev_selection)
        preferences = update_preferences(preferences, selection, reward)
        reward_history.append(reward)
        prev_selection = selection

    sorted_prefs = sorted(zip(NUMBERS, preferences), key=lambda x: x[1], reverse=True)
    top_numbers = [num for num, _ in sorted_prefs[:10]]

    return {
        "preferences": sorted_prefs,
        "reward_history": reward_history,
        "top_numbers": top_numbers
    }