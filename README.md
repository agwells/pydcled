pydcled
=======

A python program/library for controlling the [Dream Cheeky 818 LED message board](http://dreamcheeky.com/led-message-board)

Code inspired by:

* dcled: http://www.last-outpost.com/~malakai/dcled/
* dcled_ruby: https://github.com/Lewis-Clayton/dcled_ruby


#### Requirements

* Python 2.7
* PyUSB 1.0: http://walac.github.io/pyusb/
  * ... and PyUSB will require libusb. See the PyUSB website for more details.


#### Coding usage

It's an easy two-step process.

1. Instantiate a dcled.core.LED object.
  1. You can optionally pass a [curses](https://docs.python.org/2/library/curses.html) Window object to LED.__init__(). If you do, the contents of the LED will be simultaneously displayed in the terminal using curses.
2. Call the "LED.showascii()" method. This method takes two arguments.
  1. The first should be a 147-character (i.e. 21 x 7) string containing the image you want to display on the LED. Newlines are ignored, 'x' characters represent lit pixels, and all other characters represent dark pixels.
  2. If you want a different character than 'x' to represent lit pixels, you can send that as the second argument. The ruby_pydcled project, for instance, seems to prefer '*', so you might want to use that.

```
import pydcled.core
led = dcled.core.LED()

eyepic = '''
..xxx...........xxx..
.x...x.........x...x.
x.....x.......x.....x
x..x..x.......x..x..x
x.....x.......x.....x
.x...x...xxx...x...x.
..xxx.....x.....xxx..
'''

# Will display eyepic until you send a different picture or the program ends.
led.showascii(eyepic)
```

If you've read the LED's [technical manual](https://github.com/Lewis-Clayton/dcled_ruby/blob/master/USB_LED_Message_Board_-_Developer_Manual_v1.0.pdf), you may be aware that it only stays lit for around half a second after each USB message sent to it, so you have to keep pumping the state of the screen to it repeatedly. This library takes care of that for you using a background thread that refreshes the LED every 400 milliseconds, or whenever you send a new picture to it. So you don't need to worry about refreshing the LED at regular intervals. Just call LED.showascii() whenever you want the image on the LED to change. (If you'd rather control the refresh timing yourself, use the LED_untimed class.)

#### Included sample scripts

* eyes.py
  * Displays a pair of eyes that blink at random intervals. With the "-i" interactive flag, it will display the LED contents in the terminal, and pressing space will toggle it between awake and asleep.
* ledbyscreensaver.sh
  * A shell script that switches between "eyes open" and "eyes shut" depending on whether your screensaver is active or not.
* interactive.py
  * Displays a single lit pixel in the LED, which can be moved by pressing the keyboard arrow keys. The state of the LED is also displayed in the Terminal

#### TODO:

A bunch of stuff. Most notably, I haven't written any support for text yet. If you just want to use your LED to display text, your best bet is probably [dcled](http://www.last-outpost.com/~malakai/dcled/).
