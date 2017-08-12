import numpy
import sounddevice
import math


class Soundgenerator:
    """Create sounds that can be fed into sounddevice.

    All generated sound values range from -1.0 to +1.0 as this is what
    is expected.

    https://github.com/spatialaudio/python-sounddevice/issues/92#issuecomment-315096919

    """
    
    def __init__(self, samples=44100, devicenr=0):
        sounddevice.default.device = devicenr
        self.samples = samples

    def gen_random(self) -> numpy.ndarray:
        # 44100 random samples between -1 and 1
        return numpy.random.uniform(-1, 1, self.samples)
        # data = np.random.uniform(0, 100, 44100)

    def gen_sine(self) -> numpy.ndarray:
        data = numpy.empty((self.samples, sounddevice.default.channels),
                           dtype="float32")
        
        for ch in range(sounddevice.default.channels):
            for ms in range(self.samples):
                data[ms, ch] = math.sin(0.5 * ms)
                
        return data

    def gen_data(self, left_data, right_data):
        return numpy.array([left_data, right_data])


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
    sounddevice.play(sg.gen_random())
    sounddevice.wait()
    print("playing sine wave")
    sounddevice.play(sg.gen_sine())
    sounddevice.wait()
    print("finished")

if __name__ == "__main__":
    main()
