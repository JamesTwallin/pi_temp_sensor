import os
import glob
import json
from datetime import datetime, timezone

base_dir = '/sys/bus/w1/devices/'
local_output_dir = '/home/pi/Desktop/temperature_logs'
usb_output_dir = '/media/pi/USB_STICK/temperature_logs'

def read_temp():
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
    with open(device_file, 'r') as f:
        lines = f.readlines()
    if lines[0].strip()[-3:] != 'YES':
        return None
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        return float(temp_string) / 1000.0

def write_json(data, directory):
    os.makedirs(directory, exist_ok=True)
    filename = f"{data['timestamp'].replace(':', '-')}.json"
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f)
    print(f"Temperature reading saved to {filepath}")

def main():
    temp = read_temp()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    data = {
        "timestamp": timestamp,
        "temperature": round(temp, 1) if temp is not None else None
    }

    # Always write to local storage
    write_json(data, local_output_dir)

    # Try to write to USB stick
    try:
        if os.path.exists('/media/pi/USB_STICK'):
            write_json(data, usb_output_dir)
        else:
            print("USB stick not found. Data only saved locally.")
    except Exception as e:
        print(f"Error writing to USB stick: {str(e)}")

if __name__ == "__main__":
    main()
