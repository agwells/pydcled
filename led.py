import usb.core
import usb.backend.libusb1
import usb.util
import sys
import os
import time

# Python program to control the Dream Cheeky USB LED
# Code inspired by dcled: http://www.last-outpost.com/~malakai/dcled/
# and by dcled_ruby: https://github.com/Lewis-Clayton/dcled_ruby

# find our device
device = usb.core.find(
    backend = usb.backend.libusb1.get_backend(),
    idVendor = 0x1d34,
    idProduct = 0x0013
)
#print device.get_active_configuration()
device.reset()
#device.detach_kernel_driver(0)

# Sample data from the hardware developer's manual: makes a diamond
data = [
    0x00, 0x00, 0xFF,0xFE,0xFF, 0xFF,0xFD,0x7F,
    0x00, 0x02, 0xFF,0xFB,0xBF, 0xFF,0xF7,0xDF,
    0x00, 0x04, 0xFF,0xFB,0xBF, 0xFF,0xFD,0x7F,
    0x00, 0x06, 0xFF,0xFE,0xFF
]

for i in range(0,1000):
    device.ctrl_transfer(
        bmRequestType = 0x21,
        bRequest = 0x09,
        wValue = 0x0000,
        wIndex = 0x0000,
        data_or_wLength = data
    )
    time.sleep(0.4)
