import os
import glob
import json
import subprocess
from datetime import datetime, timezone

base_dir = '/sys/bus/w1/devices/'
local_output_dir = '/home/pi/Desktop/temperature_logs'

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

def find_usb_drive():
    try:
        # Run the lsblk command to list block devices
        result = subprocess.run(['lsblk', '-Jplno', 'NAME,TYPE,MOUNTPOINT'], capture_output=True, text=True)
        devices = json.loads(result.stdout)

        # Find the first mounted removable drive
        for device in devices['blockdevices']:
            if device['type'] == 'disk':
                for partition in device.get('children', []):
                    if partition['mountpoint']:
                        return partition['mountpoint']
    except Exception as e:
        print(f"Error finding USB drive: {str(e)}")
    return None

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

    # Try to write to USB drive
    usb_mount = find_usb_drive()
    if usb_mount:
        try:
            usb_output_dir = os.path.join(usb_mount, 'temperature_logs')
            write_json(data, usb_output_dir)
        except Exception as e:
            print(f"Error writing to USB drive: {str(e)}")
    else:
        print("No USB drive found. Data only saved locally.")

if __name__ == "__main__":
    main()
