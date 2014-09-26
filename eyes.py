import time
import random
import argparse
import dcled.core

# Python program to control the Dream Cheeky USB LED: http://www.dreamcheeky.com/led-message-board
# Code inspired by dcled: http://www.last-outpost.com/~malakai/dcled/
# and by dcled_ruby: https://github.com/Lewis-Clayton/dcled_ruby

# Requires PyUSB 1.0: http://walac.github.io/pyusb/

# Sample data from the hardware developer's manual: makes a diamond
diamond = [
    [0x00, 0x00, 0xFF,0xFE,0xFF, 0xFF,0xFD,0x7F,],
    [0x00, 0x02, 0xFF,0xFB,0xBF, 0xFF,0xF7,0xDF,],
    [0x00, 0x04, 0xFF,0xFB,0xBF, 0xFF,0xFD,0x7F,],
    [0x00, 0x06, 0xFF,0xFE,0xFF,],
]

teeth = [
"""
xxxxxxxxxxxxxxxxxxxxx
.xxx.xxx.xxx.xxx.xxx.
.xxx.xxx.xxx.xxx.xxx.
..x.x.x.x.x.x.x.x.x..
..x.x.x.x.x.x.x.x.x..
...xxx.xxx.xxx.xxx...
...xxx.xxx.xxx.xxx...
""",
"""
.xxx.xxx.xxx.xxx.xxx.
.xxx.xxx.xxx.xxx.xxx.
..x...x...x...x...x..
..x.x.x.x.x.x.x.x.x..
....x...x...x...x....
...xxx.xxx.xxx.xxx...
...xxx.xxx.xxx.xxx...
""",
"""
.xxx.xxx.xxx.xxx.xxx.
..x...x...x...x...x..
..x...x...x...x...x..
.....................
....x...x...x...x....
....x...x...x...x....
...xxx.xxx.xxx.xxx...
""",
"""
..x...x...x...x...x..
..x...x...x...x...x..
.....................
.....................
.....................
....x...x...x...x....
....x...x...x...x....
""",
"""
..x...x...x...x...x..
.....................
.....................
.....................
.....................
.....................
....x...x...x...x....
""",
]

kitty = []
kitty.append(
"..xxx...........xxx.." \
".x...x.........x...x." \
"x.....x.......x.....x" \
"x..x..x.......x..x..x" \
"x.....x.......x.....x" \
".x...x...xxx...x...x." \
"..xxx.....x.....xxx.."
)

kitty.append(
"....................." \
".xxxxx.........xxxxx." \
"x.....x.......x.....x" \
"x..x..x.......x..x..x" \
"x.....x.......x.....x" \
".xxxxx...xxx...xxxxx." \
"..........x.........." 
)

kitty.append(
"....................." \
"....................." \
".xxxxx.........xxxxx." \
"x..x..x.......x..x..x" \
".xxxxx.........xxxxx." \
".........xxx........." \
"..........x.........." 
)

kitty.append(
"....................." \
"....................." \
"....................." \
"xxxxxxx.......xxxxxxx" \
"....................." \
".........xxx........." \
"..........x.........." 
)

grumpy = []
grumpy.append(
"..xx.....xxx.....xx.." \
"..x.x.....x.....x.x.." \
".x..x...........x..x." \
".x.x.x.........x.x.x." \
".x...x.........x...x." \
"..x.x....xxx....x.x.." \
"..xxx...x...x...xxx.." 
)

grumpy.append(
".........xxx........." \
"..xxx.....x.....xxx.." \
".x...x.........x...x." \
".x.x.x.........x.x.x." \
".x...x.........x...x." \
"..xxx....xxx....xxx.." \
"........x...x........" 
)

grumpy.append(
".........xxx........." \
"..........x.........." \
"..xxx...........xxx.." \
".x.x.x.........x.x.x." \
"..xxx...........xxx.." \
".........xxx........." \
"........x...x........" 
)

grumpy.append(
".........xxx........." \
"..........x.........." \
"....................." \
".xxxxx.........xxxxx." \
"....................." \
".........xxx........." \
"........x...x........" 
)


human = []
human.append(
"....................." \
".xxxxx.........xxxxx." \
"x.xxx.x.......x.xxx.x" \
"x.xxx.xx.xxx.xx.xxx.x" \
"x.....x..xxx..x.....x" \
".x...x...xxx...x...x." \
"..xxx...x.x.x...xxx.." 
)

human.append(
"....................." \
"....................." \
"xxxxxxx.......xxxxxxx" \
"x.xxx.xx.xxx.xx.xxx.x" \
"x.....x..xxx..x.....x" \
".xxxxx...xxx...xxxxx." \
"........x.x.x........" 
)

human.append(
"....................." \
"....................." \
"....................." \
"xxxxxxxx.xxx.xxxxxxxx" \
"xxxxxxx..xxx..xxxxxxx" \
".........xxx........." \
"........x.x.x........" 
)

human.append(
"....................." \
"....................." \
"....................." \
"xxxxxxxx.xxx.xxxxxxxx" \
".........xxx........." \
".........xxx........." \
"........x.x.x........" 
)


single = []
single.append(
".........xxx........." \
"........x...x........" \
".......x..x..x......." \
"......x...x...x......" \
"......xx..x..xx......" \
"........x...x........" \
".........xxx........." 
)

single.append(
"........x.x.x........" \
"........xxxxx........" \
".......x..x..x......." \
"......x...x..xx......" \
"......xx..x..xx......" \
"........xxxxx........" \
"........x.x.x........" 
)

single.append(
"....................." \
"........x.x.x........" \
"........xxxxx........" \
"......xx..x..xx......" \
".......xxxxxxx......." \
"........x.x.x........" \
"....................." 
)

single.append(
"....................." \
"....................." \
"........x.x.x........" \
"......xxxxxxxxx......" \
"........x.x.x........" \
"....................." \
"....................." 
)

def blink(led, eyeset, blinktime = 0.05):
    for frame in eyeset + eyeset[::-1]:
        led.showascii(frame)
        time.sleep(blinktime)

######################################

# The available eye sets
eyesets = {
    'grumpy' : grumpy,
    'kitty'  : kitty,
    'single' : single,
    'teeth'  : teeth,
    'human'  : human
}

# Get the command-line options to decide which set of eyes to display, and open or shut
parser = argparse.ArgumentParser()
parser.add_argument(
    '-e', '--eyes', 
    default = 'kitty',
    choices = sorted(eyesets.keys()),
    help = 'Which set of eyes to show'
)
parser.add_argument(
    '--shut',
    action = 'store_true',
    help = 'Add this to display with eyes shut'
)

args = parser.parse_args()
eyes = eyesets[args.eyes]

led = dcled.core.LED()

if (args.shut):
    blinktime = 0.1

    # Blink a few times before closing your eyes
    for i in range(0, random.randint(2,4)):
        blink(led, eyes, blinktime)

    # Close your eyes (skip the first frame because we showed it during the blink
    for frame in eyes[1:]:
        led.showascii(frame)
        time.sleep(blinktime)

    # Awake
    while (1):

        # Even though the image isn't changing, we need to refresh the LED
        # about every 0.4 seconds
        led.showascii(eyes[-1])
        time.sleep(0.4)
else:
    blinktime = 0.05
    
    # Open your eyes
    for frame in eyes[::-1]:
        led.showascii(frame)
        time.sleep(blinktime)

    # Wake up by blinking a few times
    for i in range(0, random.randint(2,5)):
        blink(led, eyes, blinktime)

    # Awake
    while (1):

        # Eyes open for random duration
        for i in range (0, random.randint(0,16)):
            # Even though the image isn't changing, we need to refresh the LED
            # about every 0.4 seconds
            led.showascii(eyes[0])
            time.sleep(0.4)

        # Blink animation
        blink(led, eyes, blinktime)

