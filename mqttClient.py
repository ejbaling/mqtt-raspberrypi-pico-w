import network
import time
import ujson
import machine
from math import sin
from umqtt.simple import MQTTClient

led = machine.Pin("LED", machine.Pin.OUT)

with open('secrets.json') as fp:
    secrets = ujson.loads(fp.read())

# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = secrets['wifi']['ssid']
wifi_password = secrets['wifi']['password']

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to WiFi")

mqtt_host = secrets['mqtt']['host']
mqtt_username = secrets['mqtt']['username']
mqtt_password = secrets['mqtt']['password']
mqtt_publish_topic = "/sh/water-pump"  # The MQTT topic for your broker in Home Assistant

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = "somethingreallyrandomandunique123"

mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password)

mqtt_client.connect()

# Publish a data point to the Adafruit IO MQTT server every 3 seconds
# Note: Adafruit IO has rate limits in place, every 3 seconds is frequent
#  enough to see data in realtime without exceeding the rate limit.
counter = 0
try:
    while True:
        # Generate some dummy data that changes every loop
        sine = sin(counter)
        counter += .8
        
        # Publish the data to the topic!
        print(f'Publish {sine:.2f}')
        mqtt_client.publish(mqtt_publish_topic, str(sine))
        
        led.value(1)
        time.sleep(3)
        led.value(0)
        
        # Delay a bit to avoid hitting the rate limit
        time.sleep(3)
except Exception as e:
    print(f'Failed to publish message: {e}')
finally:
    mqtt_client.disconnect()