import RPi.GPIO as GPIO
import time
import random
import soundgen
import sounddevice
import numpy


# pin configuration
pin_taster = 40  # controlling the bird (using switch or pontentiometer)
pin_start = 38  # a switch controlling the reset/start
pin_audio1 = 36  # audio1 each time the bird is flapping
pin_audio2 = 32  # audio2 each time a wave has passed
pins_in = [pin_taster, pin_start]

sg = soundgen.Soundgenerator()

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

# Coordinate System: All values of x and y are in [-1.0, +1.0]
# distance defines step width between two coordinates x and y.
XYDISTANCE = 0.1


def xres():
    return int((2 / XYDISTANCE) + 1)


def yres():
    return int((2 / XYDISTANCE) + 1)


def setup():
    GPIO.setmode(GPIO.BOARD)
    print("setup pins in:", pins_in)

    GPIO.setup([pin_audio1, pin_audio2], GPIO.OUT)

    for p in pins_in:
        GPIO.setup(p, GPIO.IN)


def px(x, y, wait=0):
    """Draw pixel a (x,y). x and y in [-1.0, +1.0]."""

    data = sg.gen_data([x], [y])
    sounddevice.wait()
    sounddevice.play(data)

    if wait > 0:
        time.sleep(wait)


def vline(x, gap_start, gap_end):
    """Drawing a vertical line at position x. x is in [-1, +1]. A gap is drawn
    between gap_start and gap_end."""

    # holding x/y-values for points to be drawn
    xs = []
    ys = []

    i = 0
    for y in numpy.arange(-1, 1, XYDISTANCE):
        if gap_start < y < gap_end:
            continue

        xs[i] = x
        ys[i] = y

        i += 1

    data = sg.gen_data(xs, ys)
    sounddevice.wait()
    sounddevice.play(data)


def draw_bird(bird_y_pos):
    px(0, bird_y_pos)


def bird_alive(current_x, bird_y, gap_start, gap_end):
    return current_x != 0 or gap_start < bird_y < gap_end


def draw_image(image):
    """Draw the image. Image is a two dimensional array of 1s or 0s. Each
    line is drawn twice."""
    for x in range(xres() + 1):
        for y in range(yres() + 1):
            if image[y // 2][x] == 1:
                px(x, yres() - y)


def draw_points(points):
    for i in range(points):
        px(i, 0)


def beep(times):
    GPIO.output(pin_audio2, True)
    time.sleep(times)
    GPIO.output(pin_audio2, False)


def start_game():
    gap_start, gap_end = 10, 18
    bird_died = False
    points = 0
    bird = 10

    GPIO.output(pin_audio1, True)
    GPIO.output(pin_audio2, False)

    while not bird_died:
        for x in range(xres(), -1, -1):
            # handle input
            if GPIO.input(pin_taster):
                bird = min(bird + 1, yres())
            else:
                bird = max(0, bird - 1)

            if not bird_alive(x, bird, gap_start, gap_end):
                bird_died = True
                print("Ende")

                # draw world
            vline(x, gap_start, gap_end)
            draw_points(points)
            draw_bird(bird)  # must(!) be drawn last

            # wait some time
            time.sleep(0.1)

        # add point after each wave
        points += 1
        beep(0.01)

        # termine new gap for next wave
        rnd_start = random.randint(10, yres() - 15)
        if points >= 10:  # xres():
            # we are unfair here when the user gets too many points
            gap_start, gap_end = 0, 1
        else:
            gap_start, gap_end = rnd_start, rnd_start + 8

    beep(0.2)
    while not GPIO.input(pin_start):
        GPIO.output(pin_audio1, False)
        draw_image(DEAD_SCREEN)
        time.sleep(0.001)

    start_game()


if __name__ == "__main__":
    setup()
    start_game()
