# blender-addon-multi-serial-control
Allows to send  transformation properties from one or many object to one or many connected devices via independent serial ports

![blender](./Screenshot%20from%202025-03-09%2010-20-25.png)


To Debug, it's possible to take advantage ot the [dual-serial-repeater](https://github.com/n2048-creative-technology/dual-arduino-serial-repeater)



Replace USB port names

```
ls /dev/ttyUSB* /dev/ttyACM*
udevadm info -a -n /dev/ttyACM0

sudo nano /etc/udev/rules.d/99-arduino.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```


Example line:
```
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0043", ATTRS{serial}=="XXXXXXXX", SYMLINK+="arduino1", MODE="0666"
```

(name the arduinos as N2048_##)
