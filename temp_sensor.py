import os
import glob
import time
import json
from datetime import datetime, timezone

# Initialize the 1-Wire interface
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Define the directory where the sensor data is stored
base_dir = '/sys/bus/w1/devices/'

# USB stick mount point - update this to match your setup
USB_MOUNT_POINT = '/media/pi/USB_STICK'

def find_device():
    # Find the device folder that starts with '28-'
    device_folders = glob.glob(base_dir + '28*')
    if device_folders:
        return device_folders[0] + '/w1_slave'
    return None

def read_temp_raw(device_file):
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
    return None, None

def get_zulu_timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def write_to_json(data):
    timestamp = data['timestamp'].replace(':', '-')  # Replace colons for filename compatibility
    filename = f"temp_reading_{timestamp}.json"
    filepath = os.path.join(USB_MOUNT_POINT, filename)
    
    with open(filepath, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def main():
    device_file = find_device()
    if not device_file:
        print("Error: DS18B20 sensor not found. Please check your connections and ensure the sensor is properly set up.")
        return

    print("DS18B20 sensor found. Starting temperature readings...")

    try:
        while True:
            celsius, fahrenheit = read_temp(device_file)
            timestamp = get_zulu_timestamp()
            
            if celsius is not None and fahrenheit is not None:
                data = {
                    "timestamp": timestamp,
                    "temperature_celsius": round(celsius, 1),
                    "temperature_fahrenheit": round(fahrenheit, 1)
                }
                print(f"{timestamp} - Temperature: {celsius:.1f}°C | {fahrenheit:.1f}°F")
                write_to_json(data)
            else:
                print(f"{timestamp} - Error reading temperature. Retrying...")
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("Script terminated by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
