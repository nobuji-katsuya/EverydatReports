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
    shift = np.random.normal(0, 0.005)            # 時間方向のわずかなズレ
    shifted_x = np.clip(x + shift, 0, 1)
    wave = 0.2 + 0.8 * np.exp(-((shifted_x - 0.4) ** 2) / 0.01)
    wave = scale * wave + noise
    good_waves.append(wave)
good_waves = np.array(good_waves)  # shape: (M, N)

# -----------------------------
# 2. 平均 ± 3σ でエンベロープバンド生成（選択肢B）
# -----------------------------
mean = np.mean(good_waves, axis=0)
std = np.std(good_waves, axis=0)
k = 3.0
upper = mean + k * std
lower = mean - k * std

# -----------------------------
# 3. 「新しい波形」を用意（わざと一部NGっぽく）
# -----------------------------
new_wave = base.copy()
new_wave += np.random.normal(0, 0.02, N)
# 途中で圧力が高すぎる異常を混ぜる
new_wave[500:650] += 0.2

# -----------------------------
# 4. プロットして「見た目」で確認
# -----------------------------
plt.figure(figsize=(10, 6))

# 良品波形（薄いグレー）
for wave in good_waves:
    plt.plot(x, wave, color='gray', alpha=0.3, linewidth=0.7)

# エンベロープバンド（上下の帯）
plt.fill_between(x, lower, upper, color='lightblue', alpha=0.5,
                 label='Envelope band (mean ± 3σ)')

# 新しい波形（判定対象）
plt.plot(x, new_wave, color='red', linewidth=2, label='New wave')

plt.xlabel("Normalized time")
plt.ylabel("Pressure (arb. unit)")
plt.title("Envelope band and new wave")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()