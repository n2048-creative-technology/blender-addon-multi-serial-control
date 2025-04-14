#!/usr/bin/env sh

name=$1
echo $name

idVendor=`ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | grep /dev | xargs -I% udevadm info -a -n % | grep idVendor | head -1 | cut -d\" -f2`
idProduct=`ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | grep /dev | xargs -I% udevadm info -a -n % | grep idProduct | head -1 | cut -d\" -f2`
serial=`ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | grep /dev | xargs -I% udevadm info -a -n % | grep serial | head -1 | cut -d\" -f2`

echo SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"$idVendor\", ATTRS{idProduct}==\"$idProduct\", ATTRS{serial}==\"$serial\", SYMLINK+=\"/dev/N2048_$name\", MODE=\"0666\" >> /etc/udev/rules.d/99-arduino.rules

udevadm control --reload-rules

echo dev/N2048_$name added to /etc/udev/rules.d/99-arduino.rules