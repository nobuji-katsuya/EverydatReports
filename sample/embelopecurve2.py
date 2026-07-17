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
    noise = np.random.normal(0, 0.02, N)          # ランダムノイズ
    scale = 1.0 + np.random.normal(0, 0.02)       # 振幅のばらつき
    shift = np.random.normal(0, 0.005)            # 時間方向のズレ
    shifted_x = np.clip(x + shift, 0, 1)
    wave = 0.2 + 0.8 * np.exp(-((shifted_x - 0.4) ** 2) / 0.01)
    wave = scale * wave + noise
    good_waves.append(wave)

good_waves = np.array(good_waves)  # shape: (M, N)

# -----------------------------
# 2. 中央値 ± k * MAD でエンベロープバンド生成（選択肢C）
# -----------------------------
median = np.median(good_waves, axis=0)
mad = np.median(np.abs(good_waves - median), axis=0)

k = 4.0
upper = median + k * mad
lower = median - k * mad

# -----------------------------
# 3. 新しい波形（わざとNGっぽく）
# -----------------------------
new_wave = base.copy()
new_wave += np.random.normal(0, 0.02, N)
new_wave[500:650] += 0.2  # 異常を混ぜる

# -----------------------------
# 4. プロット
# -----------------------------
plt.figure(figsize=(10, 6))

# 良品波形（薄いグレー）
for wave in good_waves:
    plt.plot(x, wave, color='gray', alpha=0.3, linewidth=0.7)

# エンベロープバンド（中央値 ± MAD）
plt.fill_between(x, lower, upper, color='lightgreen', alpha=0.5,
                 label='Envelope band (median ± MAD)')

# 中央値
plt.plot(x, median, color='green', linewidth=1.5, label='Median')

# 新しい波形
plt.plot(x, new_wave, color='red', linewidth=2, label='New wave')

plt.xlabel("Normalized time")
plt.ylabel("Pressure (arb. unit)")
plt.title("Envelope band using Median ± MAD")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()