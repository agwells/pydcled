import dcled.core
import curses
import time

def genimg(cursorx, cursory):
    img = ''
    for y in range(0, 7):
        if y == cursory:
            img = img + ('.' * cursorx) + 'x' + ('.' * (20 - cursorx))
        else:
            img = img + ('.' * 21)
    return img

def mainui(stdscr = False):
    led = dcled.core.LED(stdscr)
    cursorx = 0
    cursory = 0
    while (True):
        img = genimg(cursorx, cursory)
        led.showascii(img)
        c = stdscr.getch()
        if c == curses.KEY_UP:
            cursory -= 1
            if cursory < 0:
                cursory = 6
        if c == curses.KEY_DOWN:
            cursory += 1
            if cursory > 6:
                cursory = 0
        if c == curses.KEY_RIGHT:
            cursorx += 1
            if cursorx > 20:
                cursorx = 0
        if c == curses.KEY_LEFT:
            cursorx -= 1
            if cursorx < 0:
                cursorx = 20

curses.wrapper(mainui)
