import RPi.GPIO as GPIO
import time

# 2x6 Bit
# pin 27 reserver for i2c
pins =  [37,35,33,31,29,23, #ch1
         21,19,15,13,11,7]  #ch2
#pins = [29,31,33,35,37]
#pins = [29,31,33]

def setup():
    GPIO.setmode(GPIO.BOARD)
    print("setup pins",pins)

    for p in pins:
        GPIO.setup(p, GPIO.OUT)

        
def int2bin(integer):
    b = bin(integer)
    res = []
    for c in b[2:]: #ignoring 0b... at beginning
        res.append( int(c) )

    return res
    
def test_all():
    print("testing all possible values")
    for n in range(2**len(pins)):
        r = int2bin(n)
        if len(r) != len(pins):
            # prepend 0s
            zeros = [0] * (len(pins) - len(r))
            r = zeros + r

        print(n, r)

        GPIO.output(pins, r)
        time.sleep(0.5)
    

def test_constant():
    print("testing 1s on every pin")
    for p in pins:
        GPIO.output(p, 0)
        #time.sleep(0.1)
        GPIO.output(p, 1)
        #print(p)


if __name__ == "__main__":
    setup()
    while True:
        test_all()
        #test_constant()
    GPIO.cleanup()
