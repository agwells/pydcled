import usb.core
import time
import random

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


eyes1 = \
"..xxx...........xxx.." \
".x...x.........x...x." \
"x.....x.......x.....x" \
"x..x..x.......x..x..x" \
"x.....x.......x.....x" \
".x...x...xxx...x...x." \
"..xxx.....x.....xxx.." 

eyes2 = \
"....................." \
".xxxxx.........xxxxx." \
"x.....x.......x.....x" \
"x..x..x.......x..x..x" \
"x.....x.......x.....x" \
".xxxxx...xxx...xxxxx." \
"..........x.........." 

eyes3 = \
"....................." \
"....................." \
".xxxxx.........xxxxx." \
"x..x..x.......x..x..x" \
".xxxxx.........xxxxx." \
".........xxx........." \
"..........x.........." 

eyes4 = \
"....................." \
"....................." \
"....................." \
"xxxxxxx.......xxxxxxx" \
"....................." \
".........xxx........." \
"..........x.........." 


eye1 = \
".........xxx........." \
"........x...x........" \
".......x.....x......." \
".......x..x..x......." \
".......x.....x......." \
"........x...x........" \
".........xxx........." 

eye2 = \
"....................." \
"........xxxxx........" \
".......x.....x......." \
".......x..x..x......." \
".......x.....x......." \
"........xxxxx........" \
"....................." 
         
eye3 = \
"....................." \
"....................." \
"........xxxxx........" \
".......x..x..x......." \
"........xxxxx........" \
"....................." \
"....................." 

eye4 = \
"....................." \
"....................." \
"....................." \
".......xxxxxxx......." \
"....................." \
"....................." \
"....................." 

eyeblink = [eye1, eye2, eye3, eye4, eye3, eye2, eye1]
eyesblink = [eyes1, eyes2, eyes3, eyes4, eyes3, eyes2, eyes1]

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
def sendpackets(data):
    for packet in data:
        device.ctrl_transfer(
            bmRequestType = 0x21,
            bRequest = 0x09,
            wValue = 0x0000,
            wIndex = 0x0000,
            data_or_wLength = packet
        )

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

# try:
#     device.detach_kernel_driver(0)
# except usb.core.USBError:
#     pass

def blink():
    for frame in eyesblink:
        sendpackets(parse(frame))
        time.sleep(0.05)

# Wake up by blinking a few times
for i in range(0, random.randint(2,5)):
    blink()

# Awake
while (1):

    # Eyes open for random duration
    for i in range (0, random.randint(0,16)):
        # Even though the image isn't changing, we need to refresh the LED
        # about every 0.4 seconds
        sendpackets(parse(eyes1))
        time.sleep(0.4)

    # Blink animation
    blink()

