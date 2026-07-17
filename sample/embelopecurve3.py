import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# 1. サンプル「良品波形」を作る
# -----------------------------
N = 1000          # 1波形あたりの点数
M = 20            # 良品波形本数
x = np.linspace(0, 1, N)

# ベース波形（例：立ち上がり → ピーク → 減衰）
base = 0.2 + 0.8 * np.exp(-((x - 0.4) ** 2) / 0.01)

# 良品波形：ベース + わずかなバラつき
good_waves = []
for i in range(M):
    noise = np.random.normal(0, 0.02, N)
    scale = 1.0 + np.random.normal(0, 0.02)
    shift = np.random.normal(0, 0.005)
    shifted_x = np.clip(x + shift, 0, 1)
    wave = 0.2 + 0.8 * np.exp(-((shifted_x - 0.4) ** 2) / 0.01)
    wave = scale * wave + noise
    good_waves.append(wave)

good_waves = np.array(good_waves)

# -----------------------------
# 2. 中央値 ± k * MAD でエンベロープ作成
# -----------------------------
median = np.median(good_waves, axis=0)
mad = np.median(np.abs(good_waves - median), axis=0)

k = 3.0
upper = median + k * mad
lower = median - k * mad

# -----------------------------
# 3. 移動平均で平滑化（window=15）
# -----------------------------
def moving_average(data, window=15):
    return np.convolve(data, np.ones(window)/window, mode='same')

upper_smooth = moving_average(upper, window=15)
lower_smooth = moving_average(lower, window=15)

# -----------------------------
# 4. 新しい波形（わざとNGっぽく）
# -----------------------------
new_wave = base.copy()
new_wave += np.random.normal(0, 0.02, N)
new_wave[500:650] += 0.2  # 異常を混ぜる

# -----------------------------
# 5. プロット
# -----------------------------
plt.figure(figsize=(10, 6))

# 良品波形（薄いグレー）
for wave in good_waves:
    plt.plot(x, wave, color='gray', alpha=0.3, linewidth=0.7)

# 平滑化したエンベロープバンド
plt.fill_between(x, lower_smooth, upper_smooth,
                 color='lightgreen', alpha=0.5,
                 label='Smoothed Envelope (Median ± MAD)')

# 中央値
plt.plot(x, median, color='green', linewidth=1.5, label='Median')

# 新しい波形
plt.plot(x, new_wave, color='red', linewidth=2, label='New wave')

plt.xlabel("Normalized time")
plt.ylabel("Pressure (arb. unit)")
plt.title("Smoothed Envelope band using Median ± MAD")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()