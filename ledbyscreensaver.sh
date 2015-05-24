#/bin/bash

# This script will make the LED show open eyes when your computer is active, and
# closed eyes when your screensaver comes on.

# To make it launch on startup, put this command in your startup applications list:
# bash -c "/PATH/TO/YOUR/ledbyscreensaver.sh"

eyes=${1:-kitty}
pathtoeyes="/home/aaronw/programs/pydcled/eyes.py -e $eyes"
# For Mint MATE
screensaverintf="interface=org.mate.ScreenSaver,member=ActiveChanged"
# For Gnome
#screensaverintf="interface=org.gnome.ScreenSaver,member=ActiveChanged"

dbus-monitor --session "$screensaverintf" --monitor | (

    echo "Waking up!"
    python $pathtoeyes &
    LEDPID=$!

    function clean_up {
        kill $LEDPID
        echo "LED is now powered off."
        reset
        exit
    }

    trap clean_up SIGTERM SIGINT SIGHUP

    while true; do
        read X
        if echo $X | grep "boolean true" &> /dev/null; then
            echo "Going to sleep!"
            kill $LEDPID &> /dev/null 2>&1
            python $pathtoeyes --shut &
            LEDPID=$!
        elif echo $X | grep "boolean false" &> /dev/null; then
            echo "Waking up!"
            kill $LEDPID &> /dev/null 2>&1
            python $pathtoeyes &
            LEDPID=$!
        fi
    done
)

