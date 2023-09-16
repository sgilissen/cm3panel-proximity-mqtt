# cm3panel-proximity-mqtt
GPIO PIR and DHT - Uses a PIR sensor to enable/disable the display when someone moves in or out of proximity, and posts motion and temps to an MQTT server

## Installation

### /etc/environment:
#### Needed so python script can disable/enable screen
DISPLAY=:0

### /lib/systemd/system/pirtemp.service
```
[Unit]
Description=PIR and DHT11 monitor service
Wants=systemd-networkd-wait-online.service
After=systemd-networkd-wait-online.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 <full path of your script>
Restart=on-abort

[Install]
WantedBy=multi-user.target
```


