#/bin/sh

dbus-monitor --session "interface=org.mate.ScreenSaver,member=ActiveChanged" --monitor | (
    python /home/aaronw/programs/pydcled/eyesopen.py &
    CURPY=$!
    
    while true
    do
        read X
        if echo $X | grep "boolean true" &> /dev/null; then
            echo "Going to sleep!"
            kill $CURPY
            python /home/aaronw/programs/pydcled/eyesshut.py &
            CURPY=$!
        elif echo $X | grep "boolean false" &> /dev/null; then
            echo "Waking up!"
            kill $CURPY
            python /home/aaronw/programs/pydcled/eyesopen.py &
            CURPY=$!
        fi
    done
)