import pandas as pd
import time

df = pd.DataFrame({'val': range(100000)})
df.index = pd.date_range(start='1/1/2000', periods=100000, freq='D')

# Baseline
start = time.time()
for _ in range(10):
    if isinstance(df.index, pd.DatetimeIndex):
        tarihler = [d.strftime('%Y-%m-%d') for d in df.index]
time_baseline = (time.time() - start) / 10

# Optimized
start = time.time()
for _ in range(10):
    if isinstance(df.index, pd.DatetimeIndex):
        tarihler_opt = df.index.strftime('%Y-%m-%d').tolist()
time_optimized = (time.time() - start) / 10

print(f"Baseline list comprehension: {time_baseline * 1000:.2f} ms")
print(f"Optimized pandas vectorization: {time_optimized * 1000:.2f} ms")
print(f"Speedup: {time_baseline / time_optimized:.2f}x")
