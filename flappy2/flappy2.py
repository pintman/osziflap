import RPi.GPIO as GPIO
import time
import random
import soundgen
import sounddevice
import numpy


class Display:
    """Coordinate System: All values of x and y are in [-1.0, +1.0]
    # distance defines step width between two coordinates x and y."""

    # A screen shown upon the dead of the bird.
    #               0         5         0         5
    DEAD_SCREEN = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                   [0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                   [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                   [0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0],
                   [0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
                   [0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                   [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1]]

    def __init__(self, xydistance=0.01, xymin=-1.0, xymax=1.0):
        self.soundgen = soundgen.Soundgenerator()
        self.xymin = xymin
        self.xymax = xymax
        self.xydistance = xydistance

    def xres(self):
        return int(((self.xymax - self.xymin) / self.xydistance) + 1)

    def yres(self):
        return int(((self.xymax - self.xymin) / self.xydistance) + 1)

    def px(self, x: float, y: float, wait=0):
        """Draw pixel a (x,y). x and y in [-1.0, +1.0]."""
        assert -1.0 <= x <= 1.0
        assert -1.0 <= y <= 1.0

        data = self.soundgen.gen_data([x], [y])
        sounddevice.wait()
        sounddevice.play(data)

        if wait > 0:
            time.sleep(wait)

    def vline(self, x: float, gap_start: float, gap_end: float):
        """Drawing a vertical line at position x. x is in [-1, +1]. A gap is
        drawn between gap_start and gap_end."""
        assert -1.0 <= x <= 1.0

        # holding x/y-values for points to be drawn
        xs = []
        ys = []

        i = 0
        for y in numpy.arange(-1, 1, self.xydistance):
            if gap_start < y < gap_end:
                continue

            xs[i] = x
            ys[i] = y

            i += 1

        data = self.soundgen.gen_data(xs, ys)
        sounddevice.wait()
        sounddevice.play(data)

    def draw_image(self, image):
        """Draw the image. Image is a two dimensional array of 1s or 0s. Each
        line is drawn twice."""
        for x in range(self.xres() + 1):
            for y in range(self.yres() + 1):
                if image[y // 2][x] == 1:
                    self.px(x, self.yres() - y)

    def draw_points(self, points):
        for i in range(points):
            self.px(i, 0)


class Bird:
    def __init__(self):
        self.ypos = 0

    def draw_bird(self, display: Display):
        display.px(0, self.ypos)

    def is_alive(self, current_x: float, gap_start: float, gap_end: float):
        return current_x != 0 or gap_start < self.ypos < gap_end

    def fly_up(self, ymax: float, xydistance: float):
        self.ypos = min(self.ypos + xydistance, ymax)

    def fall_down(self, xydistance: float):
        self.ypos = max(0.0, self.ypos - xydistance)


class Game:
    def __init__(self, pin_taster, pin_start, pin_audio1, pin_audio2,
                 board_mode):
        # controlling the bird (using switch or pontentiometer)
        self.pin_taster = pin_taster
        self.pin_start = pin_start  # a switch controlling the reset/start
        self.pin_audio1 = pin_audio1  # audio1 each time the bird is flapping
        self.pin_audio2 = pin_audio2  # audio2 each time a wave has passed
        self.pins_in = [pin_taster, pin_start]

        self.display = Display()
        self.bird = Bird()

        GPIO.setmode(board_mode)
        print("setup pins in:", self.pins_in)

        GPIO.setup([self.pin_audio1, self.pin_audio2], GPIO.OUT)

        for p in self.pins_in:
            GPIO.setup(p, GPIO.IN)

    def beep(self, times):
        GPIO.output(self.pin_audio2, True)
        time.sleep(times)
        GPIO.output(self.pin_audio2, False)

    def start_game(self):
        gap_start, gap_end = 0, 0 + 5 * self.display.xydistance
        bird_died = False
        score = 0

        GPIO.output(self.pin_audio1, True)
        GPIO.output(self.pin_audio2, False)

        while not bird_died:
            # count downwards
            for x in numpy.arange(self.display.xymax, self.display.xymin,
                                  -self.display.xydistance):
                # handle input
                if GPIO.input(self.pin_taster):
                    self.bird.fly_up(self.display.xymax,
                                     self.display.xydistance)
                else:
                    self.bird.fall_down(self.display.xydistance)

                if not self.bird.is_alive(x, gap_start, gap_end):
                    bird_died = True
                    print("Ende")

                # draw world
                self.display.vline(x, gap_start, gap_end)
                self.display.draw_points(score)
                self.bird.draw_bird(self.display)  # must(!) be drawn last

                # wait some time
                time.sleep(0.1)

            # add point after each wave
            score += 1
            self.beep(0.01)

            # termine new gap for next wave
            rnd_start = random.randint(10*self.display.xymin,
                                       10*self.display.xymax) / 10
            if score >= 10:  # xres():
                # we are unfair here when the user gets too many score
                gap_start, gap_end = 0, 0 + self.display.xydistance
            else:
                gap_start = rnd_start
                gap_end = rnd_start + 4 * self.display.xydistance

        self.beep(0.2)
        while not GPIO.input(self.pin_start):
            GPIO.output(self.pin_audio1, False)
            self.display.draw_image(Display.DEAD_SCREEN)
            time.sleep(0.001)

        self.start_game()


def main():
    pin_taster = 40  # controlling the bird (using switch or pontentiometer)
    pin_start = 38  # a switch controlling the reset/start
    pin_audio1 = 36  # audio1 each time the bird is flapping
    pin_audio2 = 32  # audio2 each time a wave has passed

    game = Game(pin_taster=pin_taster, pin_start=pin_start,
                pin_audio1=pin_audio1, pin_audio2=pin_audio2,
                board_mode=GPIO.BOARD)

    game.start_game()

if __name__ == "__main__":
    main()
