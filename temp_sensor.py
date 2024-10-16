import os
import glob
import csv
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
    common_mount_points = [
        '/media/pi',
        '/media/PI',
        '/mnt',
        '/media'
    ]
    for mount_point in common_mount_points:
        if os.path.exists(mount_point):
            subdirs = [os.path.join(mount_point, d) for d in os.listdir(mount_point)]
            usb_drives = [d for d in subdirs if os.path.ismount(d)]
            if usb_drives:
                return usb_drives[0]
    return None

def write_csv(data, directory):
    os.makedirs(directory, exist_ok=True)
    current_hour = data['timestamp'][:13]  # YYYY-MM-DDTHH
    filename = f"{current_hour}.csv"
    filepath = os.path.join(directory, filename)
    
    file_exists = os.path.isfile(filepath)
    
    with open(filepath, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'temperature']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(data)
    
    print(f"Temperature reading appended to {filepath}")

def main():
    temp = read_temp()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    data = {
        "timestamp": timestamp,
        "temperature": round(temp, 1) if temp is not None else None
    }

    # Always write to local storage
    write_csv(data, local_output_dir)

    # Try to write to USB drive
    usb_mount = find_usb_drive()
    if usb_mount:
        try:
            usb_output_dir = os.path.join(usb_mount, 'temperature_logs')
            write_csv(data, usb_output_dir)
        except Exception as e:
            print(f"Error writing to USB drive: {str(e)}")
    else:
        print("No USB drive found. Data only saved locally.")

if __name__ == "__main__":
    main()
