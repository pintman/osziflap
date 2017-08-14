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
        data = numpy.empty((self.samples, 2))

        for ms in range(self.samples):
            data[ms, 0] = math.sin(0.5 * ms)
            data[ms, 1] = math.sin(0.5 * ms+0.45)
                
        return data

    def gen_data(self, left_data, right_data):
        assert len(left_data) == len(right_data)
        
        a = numpy.empty((len(left_data), 2))
        for i in range(len(left_data)):
            a[i, 1] = left_data[i]
            a[i, 0] = right_data[i]
            
        return a


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
    sg = Soundgenerator(samples=100)

    #print("playing random noise")
    #sounddevice.play(sg.gen_random())
    #sounddevice.wait()
    print("playing sine wave")
    data = sg.gen_sine()
    while True:        
        sounddevice.play(data)
        sounddevice.wait()
    print("finished")

if __name__ == "__main__":
    main()
