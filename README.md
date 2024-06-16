# mqtt-raspberrypi-pico-w
MQTT on Raspberry Pi Pico W

Development IDE: Thonny (thonny.org)

## Setup:
* Add and configure the MQTT broker in Home Assistant.

## secrets.json
A file in the project's root directory that stores clear text credentials such as username, password and wifi access. Not in github, saved in computer and the board. Create a separate credentials for use in this project, do not use your existing credentials.

`{
  "mqtt": {
    "host": "10.0.0.120",
    "username": "mqtt-user",
    "password": "Ng7tov!KhVv3"
  },
  "wifi": {
    "ssid": "SPARK-U77QV8",
    "password": "DFLEE6YMVV"
  }
}`

## References:
* https://core-electronics.com.au/guides/getting-started-with-mqtt-on-raspberry-pi-pico-w-connect-to-the-internet-of-things/
* https://stfn.pl/blog/22-pico-battery-level/
* https://www.youtube.com/watch?v=vO_2XWJDF70&ab_channel=CrazyCoupleDIY
* https://www.youtube.com/watch?v=mj2kMD0LCR4&ab_channel=CoreElectronics
