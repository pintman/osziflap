import RPi.GPIO as GPIO
import time
import random
#import pygame.mixer

# pin config
pins_ch1 = [33,31,29,23]   # x-resolution: 2**len(pin...)
pins_ch2 = [19,15,13,11,7] # y-resolution: 2**len(pin...)
pins = pins_ch1 + pins_ch2
pin_taster = 40
pin_start = 38
pin_audio1 = 36
pin_audio2 = 32
pins_in = [pin_taster,pin_start]

#snd_flap = pygame.mixer.Sound("snd_flap.wav")
#snd_gull = pygame.mixer.Sound("snd_gull.wav")

# bird 
#bird = 10
#points = 0

#               0         5         0         5
DEAD_SCREEN = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
               [0,0,1,1,0,0,1,1,1,0,0,0,0,0,0,0],
               [0,1,0,1,1,1,1,0,0,1,0,0,0,0,0,0],
               [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
               [0,0,0,1,1,0,0,0,0,0,0,1,1,1,1,0],
               [0,0,1,1,0,1,1,0,0,1,1,1,0,0,1,0],
               [0,0,1,0,0,0,1,1,1,1,1,0,0,0,0,0],
               [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0],
               [1,1,1,0,0,1,0,0,1,0,0,1,0,0,1,0],
               [0,1,0,0,1,0,1,0,0,0,0,1,0,0,1,0],
               [0,1,0,0,0,1,0,0,0,0,0,1,1,0,1,1]]                             

def setup():
    GPIO.setmode(GPIO.BOARD)
    print("setup pins out:",pins, "in:", pins_in)
    print("resolution", 2**len(pins_ch1), "x", 2**len(pins_ch2))

    for p in pins:
        GPIO.setup(p, GPIO.OUT)
    GPIO.setup([pin_audio1, pin_audio2], GPIO.OUT)
    
    for p in pins_in:
        GPIO.setup(p, GPIO.IN)
        
        
def int2bin(integer):
    b = bin(integer)
    res = []
    for c in b[2:]: #ignoring 0b... at beginning
        res.append( int(c) )

    return res

def xres():
    return 2**len(pins_ch1)-1

def yres():
    return 2**len(pins_ch2)-1


def test_all():
    #print("testing all possible values")
    for n in range(2**len(pins)):
        r = int2bin(n)
        if len(r) != len(pins):
            # prepend 0s
            zeros = [0] * (len(pins) - len(r))
            r = zeros + r

        #print(n, r)

        GPIO.output(pins, r)
        #time.sleep(0.01)
    
def test_constant():
    print("testing 1s on every pin")
    for p in pins:
        GPIO.output(p, 0)
        #time.sleep(0.1)
        GPIO.output(p, 1)
        #print(p)

def px(x,y):
    xbin = int2bin(x)
    ybin = int2bin(y)
    
    zeros = [0] * (len(pins_ch1) - len(xbin))
    xbin = zeros + xbin

    zeros = [0] * (len(pins_ch2) - len(ybin))
    ybin = zeros + ybin
    GPIO.output(pins, xbin+ybin)

def vline(x, gap_start,gap_end):
    for y in range(yres()):
        if gap_start < y < gap_end:
            continue
        
        px(x,y)
        
def draw_bird(bird_y_pos):
    px(0,bird_y_pos)


def bird_alive(current_x, bird_y, gap_start, gap_end):
    return current_x != 0 or gap_start < bird_y < gap_end

def draw_image(image):
    for x in range(xres()+1):
        for y in range(yres()+1):
            if image[y // 2][x] == 1:
                px(x,yres() - y)
    

def draw_points(points):
    for i in range(points):
        px(i, 0)

def beep(times):
    GPIO.output(pin_audio2, True)
    time.sleep(times)
    GPIO.output(pin_audio2, False)
                
def start_game():
    gap_start, gap_end = 10,18    
    bird_died = False
    points = 0
    bird = 10

    GPIO.output(pin_audio1, True)
    GPIO.output(pin_audio2, False)

    while not bird_died:            
        for x in range(xres(),-1,-1):
            # handle input
            if GPIO.input(pin_taster):
                bird = min(bird+1, yres())
            else:
                bird = max(0, bird-1)
                
            if not bird_alive(x, bird, gap_start,gap_end):
                bird_died = True
                print("Ende")    

            # draw world
            vline(x, gap_start,gap_end)
            draw_points(points)
            draw_bird(bird) # must(!) be drawn last

            # wait some time
            time.sleep(0.1)
            
        points += 1
        beep(0.01)
        
        rnd_start = random.randint(10, yres()-15)
        if points >= 10: # xres():
            gap_start, gap_end = 0,1
        else:
            gap_start, gap_end = rnd_start, rnd_start+5

    beep(0.2)
    while not GPIO.input(pin_start):
        GPIO.output(pin_audio1, False)
        draw_image(DEAD_SCREEN)
        time.sleep(0.001)
        
    start_game()
            

if __name__ == "__main__":
    setup()
    start_game()
    
