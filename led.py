import usb.core
import time
import random
import argparse

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

def parse(screen):
    # strip out all newlines, in case they were using those to format the string
    screen = screen.replace("\n", '').lower()
    rows = []
    for i in range(7):
        rowbytes = []
        # Grab a slice of 21 characters, and pad it out to 24 by adding three 'x's to the end
        row = screen[(0+i*21):(21+i*21)] + '...'
        # Now grap slices of that, 8 characters at a time, and convert them to bytes
        bytenum = 0
        byteval = 0
#        print "row: " + row
        for j in range(24):
            bitnum = j % 8
            if (row[j] != 'x'):
                bitval = 2 ** bitnum
            else:
                bitval = 0
            byteval += bitval
#            print "char {0} = {1}; bitval = {2}; byteval = {3} ({3:X})".format((j), row[j], bitval, byteval)
            
            if bitnum == 7:
                bytenum += 1
                rowbytes.insert(0, byteval)
                byteval = 0
        rows.append(rowbytes)
    
    #Add an empty "row 8" to round off the size of the fourth packet
    rows.append([0xFF] * 3)

    packets = []
    for i in range(0,7,2):
        packet = []
        # brightness (0, 1, or 2; 0 = brightest)
        packet.append(0)
        # row number
        packet.append(i)
        for j in range(2):
            for k in range(3):
                packet.append(rows[i+j][k])
        packets.append(packet)
    return packets
#        print "\n"

# Data should be an array of packets ready to send to the device
def sendtoled(screen):
    global device
    
    data = parse(screen)
    for packet in data:
        device.ctrl_transfer(
            bmRequestType = 0x21,
            bRequest = 0x09,
            wValue = 0x0000,
            wIndex = 0x0000,
            data_or_wLength = packet
        )

def usbinit():
    global device
    
    # find our device
    device = usb.core.find(
    #    backend = usb.backend.libusb0.get_backend(),
        idVendor = 0x1d34,
        idProduct = 0x0013
    )

    detachkerneldriver = True

    # Check whether we need to detach the kernel driver
    try:
        if device.is_kernel_driver_active(0) == False:
            detachkerneldriver = False
    # In some supported pyusb backend libraries, this method isn't implemented
    # In which case, we may as well just try to detach the kernel driver.
    except NotImplementedError:
        detachkerneldriver = True

    if detachkerneldriver == True:
        try:
            device.detach_kernel_driver(0)
        # If we're trying to detach the kernel driver with no information (because
        # the checking method wasn't implemented), it'll throw this error
        except usb.core.USBError:
            pass


def blink(eyeset, blinktime = 0.05):
    for frame in eyeset + eyeset[::-1]:
        sendtoled(frame)
        time.sleep(blinktime)

######################################

# The available eye sets
eyesets = {
    'grumpy' : grumpy,
    'kitty'  : kitty,
    'single' : single,
    'teeth'  : teeth
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

usbinit()

if (args.shut):
    blinktime = 0.1

    # Blink a few times before closing your eyes
    for i in range(0, random.randint(2,4)):
        blink(eyes, blinktime)

    # Close your eyes (skip the first frame because we showed it during the blink
    for frame in eyes[1:]:
        sendtoled(frame)
        time.sleep(blinktime)

    # Awake
    while (1):

        # Even though the image isn't changing, we need to refresh the LED
        # about every 0.4 seconds
        sendtoled(eyes[-1])
        time.sleep(0.4)
else:
    blinktime = 0.05
    
    # Open your eyes
    for frame in eyes[::-1]:
        sendtoled(frame)
        time.sleep(blinktime)

    # Wake up by blinking a few times
    for i in range(0, random.randint(2,5)):
        blink(eyes, blinktime)

    # Awake
    while (1):

        # Eyes open for random duration
        for i in range (0, random.randint(0,16)):
            # Even though the image isn't changing, we need to refresh the LED
            # about every 0.4 seconds
            sendtoled(eyes[0])
            time.sleep(0.4)

        # Blink animation
        blink(eyes, blinktime)

