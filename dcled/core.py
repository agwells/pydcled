import usb.core
import curses
import re
import multiprocessing
import atexit

class LED_untimed(object):
    
    DeviceVendor = 0x1d34
    DeviceProduct = 0x0013
    ledheight = 7
    ledwidth = 21
    
    demodiamond = [
    [0x00, 0x00, 0xFF,0xFE,0xFF, 0xFF,0xFD,0x7F,],
    [0x00, 0x02, 0xFF,0xFB,0xBF, 0xFF,0xF7,0xDF,],
    [0x00, 0x04, 0xFF,0xFB,0xBF, 0xFF,0xFD,0x7F,],
    [0x00, 0x06, 0xFF,0xFE,0xFF,],
]

    
    def _acquiredevice(self):
        # find our device
        self.device = usb.core.find(
        #    backend = usb.backend.libusb0.get_backend(),
            idVendor = self.DeviceVendor,
            idProduct = self.DeviceProduct
        )
    
        detachkerneldriver = True
    
        # Check whether we need to detach the kernel driver
        try:
            if self.device.is_kernel_driver_active(0) == False:
                detachkerneldriver = False
        # In some supported pyusb backend libraries, this method isn't implemented
        # In which case, we may as well just try to detach the kernel driver.
        except NotImplementedError:
            detachkerneldriver = True
    
        if detachkerneldriver == True:
            try:
                self.device.detach_kernel_driver(0)
            # If we're trying to detach the kernel driver with no information (because
            # the checking method wasn't implemented), it'll throw this error
            except usb.core.USBError:
                pass
        
        self.running = True

    def __init__(self, cursesscreen = False):
        self.device = False
        self.brightness = 0
        self.running = False
        self._acquiredevice()
        self.currentimage = ''.ljust(self.ledheight * self.ledwidth, ' ')
        if cursesscreen:
            self.usecurses = True
            self.stdscr = cursesscreen
            curses.use_default_colors()
            # Code for changing the color
#             if (curses.can_change_color()):
#                 curses.init_color(0, 0, 0, 0)
#                 curses.init_pair(1, curses.COLOR_RED, 0)
#             else:
#                 curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        else:
            self.usecurses = False

    # Takes an ascii representation of the screen, and converts it into a set of bytes
    # suitable to send via USB
    def packascii(self, screen, litchar='x'):
        # strip out all newlines, in case they were using those to format the string
        screen = screen.replace("\n", '').lower()
#        print screen
        widthmult = 4
        offpixel = ' ' * widthmult
        onpixel = '@' + (' ' * (widthmult - 1))
        currentimage = screen[:(self.ledheight * self.ledwidth)].ljust((self.ledheight * self.ledwidth), ' ')
        currentimage = re.sub('[^'+litchar+']', offpixel, currentimage)
        currentimage = currentimage.replace(litchar, onpixel)
        # re-insert newlines after every 21 characters
        currentimage = '\n'.join(currentimage[i:i + self.ledwidth * widthmult] for i in xrange(0, self.ledheight * self.ledwidth * widthmult, self.ledwidth * widthmult))
        self.currentimage = currentimage
        
        rows = []
        for i in range(self.ledheight):
            rowbytes = []
            # Grab a slice of 21 characters, and pad it out to 24 by adding three 'x's to the end
            row = screen[(0+i*self.ledwidth):(self.ledwidth + i * self.ledwidth)] + '...'
            # Now grap slices of that, 8 characters at a time, and convert them to bytes
            bytenum = 0
            byteval = 0
            for j in range(24):
                bitnum = j % 8
                if (row[j] != litchar):
                    bitval = 2 ** bitnum
                else:
                    bitval = 0
                byteval += bitval
                
                if bitnum == 7:
                    bytenum += 1
                    rowbytes.insert(0, byteval)
                    byteval = 0
            rows.append(rowbytes)
        
        #Add an empty "row 8" to round off the size of the fourth packet
        rows.append([0xFF] * 3)
    
        packets = []
        for i in range(0, self.ledheight, 2):
            packet = []
            # brightness (0, 1, or 2; 0 = brightest)
            packet.append(self.brightness)
            # row number
            packet.append(i)
            for j in range(2):
                for k in range(3):
                    packet.append(rows[i+j][k])
            packets.append(packet)
        return packets
    #        print "\n"

    # Data should be an array of packets ready to send to the device
    def sendtoled(self, data):
        for packet in data:
            self.device.ctrl_transfer(
                bmRequestType = 0x21,
                bRequest = 0x09,
                wValue = 0x0000,
                wIndex = 0x0000,
                data_or_wLength = packet
            )
        if (self.usecurses):
            self.stdscr.addstr(0, 0, self.currentimage, curses.A_BOLD)
            # Code for showing it in color
#            self.stdscr.addstr(0, 0, self.currentimage, curses.color_pair(1))
            self.stdscr.refresh()

    def showascii(self, screen, litchar='x'):
        self.sendtoled(self.packascii(screen, litchar))


class LED(object):
    # How long to wait (in seconds) between refreshing the USB
    refreshrate = 0.4
    
    def close(self):
        self.process.terminate()
    
    def showascii(self, screen):
        self.pipesend.send(screen)
    
    def _run(self, piperecv, cursesscr):
        try:
            led = LED_untimed(cursesscr)
            # Initialize screen to empty
            showonscr = '.' * (LED_untimed.ledheight * LED_untimed.ledwidth)
            while True:
                led.showascii(showonscr)
                ready = piperecv.poll(self.refreshrate)
                if (ready):
                    showonscr = piperecv.recv()
        except (KeyboardInterrupt, SystemExit):
            quit()
    
    def __init__(self, cursesscr = False):
        self.pipesend, piperecv = multiprocessing.Pipe()
        self.process = multiprocessing.Process(target=LED._run, args=(self, piperecv, cursesscr))
        self.process.daemon = True
        self.process.start()
        atexit.register(self.close)
