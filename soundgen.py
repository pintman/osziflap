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

"""Accessing the audio jack on the pi:
https://raspberrypi.stackexchange.com/questions/49600/how-to-output-audio-signals-through-gpio


BCM2835 Peripherals
http://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2835/BCM2835-ARM-Peripherals.pdf

On recent Pis the audio jack output is provided by PWM channels 0 and
1. PWM channel 0 is fed to GPIO40 which is connected to the (stereo)
right channel, and PWM channel 1 is fed to GPIO45 which is connected
to the (stereo) left channel.

These PWM channels may additionally be fed to user accessible GPIO.

PWM channel 0 may be routed to GPIO12 and GPIO18.

PWM channel 1 may be routed to GPIO13 and GPIO19.

You route PWM to a GPIO by setting a particular GPIO mode as follows:

    GPIO12 - set mode ALT0
    GPIO13 - set mode ALT0
    GPIO18 - set mode ALT5
    GPIO19 - set mode ALT5

See page 102 of the Broadcom spec reference above.

"""
    
    
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
