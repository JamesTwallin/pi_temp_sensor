import os
import glob
import json
from datetime import datetime, timezone

base_dir = '/sys/bus/w1/devices/'
output_dir = '/home/pi/Desktop/temperature_logs'

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

def main():
    temp = read_temp()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    data = {
        "timestamp": timestamp,
        "temperature": round(temp, 1) if temp is not None else None
    }

    os.makedirs(output_dir, exist_ok=True)
    filename = f"{timestamp.replace(':', '-')}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        json.dump(data, f)

    print(f"Temperature reading saved to {filepath}")

if __name__ == "__main__":
    main()
