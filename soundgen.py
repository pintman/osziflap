import numpy as np
import sounddevice as sd
import math


class Soundgenerator:
    def __init__(self, samples=44100, chan=2, devicenr=0):
        sd.default.device = devicenr
        self.chan = chan
        self.samples = samples

    def gen_random(self):
        # 44100 random samples between -1 and 1
        return np.random.uniform(-1, 1, self.samples)
        # data = np.random.uniform(0, 100, 44100)

    def gen_sine(self):
        data = np.empty((self.samples, self.chan),
                        dtype="float32")
        
        for ch in range(self.chan):
            for ms in range(self.samples):
                data[ms, ch] = math.sin(0.5 * ms)
                
        return data

    
def main():
    sg = Soundgenerator()

    print("playing random noise")
    sd.play(sg.gen_random())
    sd.wait()
    print("playing sine wave")
    sd.play(sg.gen_sine())
    sd.wait()
    print("finished")

            
if __name__ == "__main__":
    main()
