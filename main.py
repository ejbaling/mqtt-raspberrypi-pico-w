import network
import time
import ujson
import machine
from math import sin
from umqtt.simple import MQTTClient
from machine import ADC

# Internal temperature sensor is connected to ADC channel 4
temp_sensor = ADC(4)

def read_internal_temperature():
    # Read the raw ADC value
    adc_value = temp_sensor.read_u16()

    # Convert ADC value to voltage
    voltage = adc_value * (3.3 / 65535.0)

    # Temperature calculation based on sensor characteristics
    temperature_celsius = 27 - (voltage - 0.706) / 0.001721

    return temperature_celsius

def celsius_to_fahrenheit(temp_celsius): 
    temp_fahrenheit = temp_celsius * (9/5) + 32 
    return temp_fahrenheit

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

try:
    while True:
        # Reading and printing the internal temperature
        temperatureC = read_internal_temperature()
        temperatureF = celsius_to_fahrenheit(temperatureC)
        print("Internal Temperature:", temperatureC, "°C")
        # print("Internal Temperature:", temperatureF, "°F")
        
        # Publish the data to the topic!
        mqtt_client.publish(mqtt_publish_topic, str(temperatureC))
        
        led.value(1)
        time.sleep(2)
        led.value(0)
        
        # Delay a bit to avoid hitting the rate limit
        time.sleep(3)
except Exception as e:
    print(f'Failed to publish message: {e}')
finally:
    mqtt_client.disconnect()
    led.value(0)