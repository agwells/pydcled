#/bin/sh

eyes=kitty

dbus-monitor --session "interface=org.mate.ScreenSaver,member=ActiveChanged" --monitor | (

    echo "Waking up!"
    python /home/aaronw/programs/pydcled/led.py -e $eyes &
    LEDPID=$!

    function clean_up {
        kill $LEDPID
        echo "LED is now powered off."
        exit
    }

    trap clean_up SIGTERM SIGINT SIGHUP

    while true; do
        read X
        if echo $X | grep "boolean true" &> /dev/null; then
            echo "Going to sleep!"
            kill $LEDPID &> /dev/null 2>&1
            python /home/aaronw/programs/pydcled/led.py -e $eyes --shut &
            LEDPID=$!
        elif echo $X | grep "boolean false" &> /dev/null; then
            echo "Waking up!"
            kill $LEDPID &> /dev/null 2>&1
            python /home/aaronw/programs/pydcled/led.py -e $eyes &
            LEDPID=$!
        fi
    done
)

