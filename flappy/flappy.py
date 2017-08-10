import RPi.GPIO as GPIO
import time
import random

# import pygame.mixer

# pin configuration
pins_ch1 = [33, 31, 26, 23]
pins_ch2 = [19, 15, 13, 11, 16]
pins = pins_ch1 + pins_ch2

pin_taster = 40  # controlling the bird (using switch or pontentiometer)
pin_start = 38  # a switch controlling the reset/start
pin_audio1 = 36  # audio1 each time the bird is flapping
pin_audio2 = 32  # audio2 each time a wave has passed
pins_in = [pin_taster, pin_start]

# snd_flap = pygame.mixer.Sound("snd_flap.wav")
# snd_gull = pygame.mixer.Sound("snd_gull.wav")

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

# cache for binary representations of integer numbers. Using this
# cache for faster lookup during rendering.
int2bin_cache = {}


def setup():
    GPIO.setmode(GPIO.BOARD)
    print("setup pins out:", pins, "in:", pins_in)
    print("resolution", 2 ** len(pins_ch1), "x", 2 ** len(pins_ch2))

    for p in pins:
        GPIO.setup(p, GPIO.OUT)
    GPIO.setup([pin_audio1, pin_audio2], GPIO.OUT)

    for p in pins_in:
        GPIO.setup(p, GPIO.IN)


def int2bin(integer):
    b = bin(integer)
    res = []
    for c in b[2:]:  # ignoring 0b... at beginning
        res.append(int(c))

    return res


def xres():
    return 2 ** len(pins_ch1) - 1


def yres():
    return 2 ** len(pins_ch2) - 1


def test_all():
    # print("testing all possible values")
    for n in range(2 ** len(pins)):
        r = int2bin(n)
        if len(r) != len(pins):
            # prepend 0s
            zeros = [0] * (len(pins) - len(r))
            r = zeros + r

        # print(n, r)

        GPIO.output(pins, r)
        # time.sleep(0.01)


def test_constant():
    print("testing 1s on every pin")
    for p in pins:
        GPIO.output(p, 0)
        # time.sleep(0.1)
        GPIO.output(p, 1)
        # print(p)


def px(x, y, wait=0):
    if x in int2bin_cache and y in int2bin_cache:
        # numbers found in cache -> using them
        xbin = int2bin_cache[x]
        ybin = int2bin_cache[y]

    else:
        # numbers not found in cache -> computing them and inserting
        # them into the cache.
        xbin = int2bin(x)
        ybin = int2bin(y)

        # prepending zeros to match number of pins
        zeros = [0] * (len(pins_ch1) - len(xbin))
        xbin = zeros + xbin
        zeros = [0] * (len(pins_ch2) - len(ybin))
        ybin = zeros + ybin

        int2bin_cache[x] = xbin
        int2bin_cache[y] = ybin

    GPIO.output(pins, xbin + ybin)
    if wait > 0:
        time.sleep(wait)


def vline(x, gap_start, gap_end):
    """Drawing a vertical line. A gap is drawn between gap_start and gap_end."""
    for y in range(yres()):
        if gap_start < y < gap_end:
            continue

        px(x, y)


def draw_bird(bird_y_pos):
    px(0, bird_y_pos)


def bird_alive(current_x, bird_y, gap_start, gap_end):
    return current_x != 0 or gap_start < bird_y < gap_end


def draw_image(image):
    """The the image. Image is a two dimensional array of 1s or 0s. Each
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
    # while True:
    #    test_all()
    start_game()
