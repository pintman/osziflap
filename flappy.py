import RPi.GPIO as GPIO
import time

# 2x5 Bit
pins_ch1 = [33,31,29,23]   # x-resolution: 2**len(pin...)
pins_ch2 = [19,15,13,11,7] # y-resolution: 2**len(pin...)
pins = pins_ch1 + pins_ch2
pin_taster = 40

bird = 10

#pins =  [33,31,29,23, #ch1
#         19,15,13,11,7]  #ch2
#pins = [29,31,33,35,37]
#pins = [29,31,33]

def setup():
    GPIO.setmode(GPIO.BOARD)
    print("setup pins",pins)
    print("resolution", 2**len(pins_ch1), "x", 2**len(pins_ch2))

    for p in pins:
        GPIO.setup(p, GPIO.OUT)
    GPIO.setup(pin_taster, GPIO.IN)

        
def int2bin(integer):
    b = bin(integer)
    res = []
    for c in b[2:]: #ignoring 0b... at beginning
        res.append( int(c) )

    return res

def xres():
    return 2**len(pins_ch1)

def yres():
    return 2**len(pins_ch2)


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
    for y in range(2**len(pins_ch2)):
        if gap_start < y < gap_end:
            continue
        
        px(x,y)
        
def draw_bird():
    px(0,bird)


def bird_alive(current_x, gap_start, gap_end):
    return x != 0 or gap_start < bird < gap_end

def draw_final_screen(image):
    for y in range(
    pass
    

if __name__ == "__main__":
    setup()
    gap_start, gap_end = 10,18    
    maxx = 2**len(pins_ch1)-1
    bird_died = False
    points = 0

    while not bird_died:            
        for x in range(maxx,-1,-1):
            # handle input
            if GPIO.input(pin_taster):
                bird = min(bird+1, 2**len(pins_ch2)-1)
            else:
                bird = max(0, bird-1)
                
            if not bird_alive(x, gap_start,gap_end):
                bird_died = True
                print("Ende")    

            # draw world
            vline(x, gap_start,gap_end)
            draw_bird() # must(!) be drawn last

            # wait some time
            time.sleep(0.05)
            
        points += 1
        
    draw_final_screen()

            
    GPIO.cleanup()
