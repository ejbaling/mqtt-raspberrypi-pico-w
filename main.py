import json
import network
import time
import ujson
import machine
from math import sin
from umqtt.simple import MQTTClient
from machine import ADC
from machine import Pin
import utime
trigger = Pin(20, Pin.OUT)
echo = Pin(21, Pin.IN)

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

def connect_to_mqtt(mqtt_client_id, mqtt_host, mqtt_username, mqtt_password):
    mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password)
    mqtt_client.connect()
    return mqtt_client

led = machine.Pin("LED", machine.Pin.OUT)

with open('secrets.json') as fp:
    secrets = ujson.loads(fp.read())

# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = secrets['wifi']['ssid']
wifi_password = secrets['wifi']['password']

# Connect to WiFi (loop indefinitely until connected)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
while (wlan.isconnected() == False):
    print('Attempting to connect to WiFi...')
    try:
        wlan.connect(wifi_ssid, wifi_password)
    except Exception as e:
        print(f"WiFi connect exception: {e}")

    # Wait up to 10 seconds for connection
    for _ in range(10):
        if wlan.isconnected() == True:
            break
        time.sleep(1)
    
    if wlan.isconnected() == False:
        print('WiFi not connected, retrying...')
        # Disconnect to reset state before next attempt
        try:
            wlan.disconnect()
        except Exception as e:
            print(f"WiFi disconnect exception: {e}")

        time.sleep(5)  # Always wait before next attempt
        
print("Connected to WiFi")

mqtt_host = secrets['mqtt']['host']
mqtt_username = secrets['mqtt']['username']
mqtt_password = secrets['mqtt']['password']
mqtt_publish_topic = "/sh/water-pump"  # The MQTT topic for your broker in Home Assistant

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = "somethingreallyrandomandunique123"

if wlan.isconnected() == True:
    mqtt_client = connect_to_mqtt(mqtt_client_id, mqtt_host, mqtt_username, mqtt_password)

while True:
    try:
        # Reading and printing the internal temperature
        temperatureC = read_internal_temperature()
        temperatureF = celsius_to_fahrenheit(temperatureC)
        print("Internal Temperature:", temperatureC, "°C")
        # print("Internal Temperature:", temperatureF, "°F")
        
        # Publish the data to the topic!
        mqtt_client.publish(mqtt_publish_topic, str(temperatureC))
        
        # Get tank water level
        trigger.low()
        utime.sleep_us(2)
        trigger.high()
        utime.sleep_us(5)
        trigger.low()
        while echo.value() == 0:
           signaloff = utime.ticks_us()
        while echo.value() == 1:
           signalon = utime.ticks_us()
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        print("The distance from object is ",distance,"cm")
        mqtt_client.publish("/sh/water-distance", json.dumps({"ClientId": mqtt_client_id, "Distance": distance, "Unit": "cm"}))
        
        led.value(1)
        time.sleep(2)
        led.value(0)
        
    except Exception as e:
        print(f'Failed to publish message: {e}')
        led.value(0)
        try:
            wlan.disconnect()
            wlan.connect(wifi_ssid, wifi_password)
        except Exception as e:
            print(f'Failed to connect to WiFi: {e}')
        
        count = 0
        while (wlan.isconnected() == False) and (count != 10):
            print('Waiting for connection...')
            count+=1
            print(f'count: {count}')
            time.sleep(1)
        if wlan.isconnected() == True:
            print("Connected to WiFi")
        try:
            mqtt_client = connect_to_mqtt(mqtt_client_id, mqtt_host, mqtt_username, mqtt_password)
            time.sleep(1)
        except Exception as e:
            print(f'Failed to connect to mqtt: {e}')
    finally:
        # Delay a bit to avoid hitting the rate limit
        time.sleep(3)
        

