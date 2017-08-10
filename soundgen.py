import numpy as np
import sounddevice as sd
import math

print("config sound device")
sd.default.device = 0

# sound output must be switched to analog

# 44100 random samples between -1 and 1
# data = np.random.uniform(-1, 1, 44100)
# data = np.random.uniform(0, 100, 44100)
data = np.empty((44100, 2), dtype="float32")

for ch in [0, 1]:
    for ms in range(44100):
        data[ms, ch] = math.sin(0.5 * ms)

print("sending np array")
sd.play(data)
sd.wait()
print("finished")
