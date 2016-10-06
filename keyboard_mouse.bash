#!/bin/bash

trap '' TERM

exec 0>&- # close stdin
exec 1>&- # close stdout
exec 2>&- # close stderr
exec 3>&- # close stderr
exec 7>&- # close stderr

logger $$  `ls /proc/self/fd`

script=$0
if [ $# -eq 0 ]; then
  setsid nohup $script intermediate > /dev/null & disown -h
  exit
else
  if [ "$1" == "intermediate" ]; then
    setsid $script final & disown -h
    exit
  fi
fi
#if [ $# -eq 0 ]; then
#  exec 0>&- # close stdin
#  exec 1>&- # close stdout
#  exec 2>&- # close stderr
#  setsid $script background & disown -h
#  exit
#fi

logger "Udev script execution defered..."
sleep 1
export DISPLAY=":0.0"
logger "What a lovely day! Sanitizing keyboard and mouse X settings... $# ($1)"

xinput list | grep -i mouse | while read line; do
  id=`echo $line | sed -e 's/^.*id=\([0-9]*.\).*$/\1/'`
  xinput set-ptr-feedback $id 4 1 1
done

setxkbmap -option grp:shift_caps_switch,caps:ctrl_modifier
xset r rate 200 60
xset m 0
