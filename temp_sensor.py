import os
import glob
import csv
from datetime import datetime, timezone
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_dir = '/sys/bus/w1/devices/'
local_output_dir = '/home/pi/Desktop/temperature_logs'

def read_temp():
    logging.info("Starting temperature reading")
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
    logging.debug(f"Reading from device file: {device_file}")
    with open(device_file, 'r') as f:
        lines = f.readlines()
    if lines[0].strip()[-3:] != 'YES':
        logging.warning("CRC check failed, temperature reading may be unreliable")
        return None
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp = float(temp_string) / 1000.0
        logging.info(f"Temperature read: {temp}°C")
        return temp
    logging.error("Failed to parse temperature data")
    return None

def find_usb_drive():
    logging.info("Searching for USB drive")
    common_mount_points = [
        '/media/pi',
        '/media/PI',
        '/mnt',
        '/media'
    ]
    for mount_point in common_mount_points:
        logging.debug(f"Checking mount point: {mount_point}")
        if os.path.exists(mount_point):
            subdirs = [os.path.join(mount_point, d) for d in os.listdir(mount_point)]
            usb_drives = [d for d in subdirs if os.path.ismount(d)]
            if usb_drives:
                logging.info(f"USB drive found: {usb_drives[0]}")
                return usb_drives[0]
    logging.warning("No USB drive found")
    return None

def write_csv(data, directory):
    logging.info(f"Writing data to CSV in directory: {directory}")
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
            logging.info(f"Created new CSV file: {filepath}")
        
        writer.writerow(data)
    
    logging.info(f"Temperature reading appended to {filepath}")

def main():
    logging.info("Starting main function")
    temp = read_temp()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    data = {
        "timestamp": timestamp,
        "temperature": round(temp, 1) if temp is not None else None
    }
    logging.info(f"Data prepared: {data}")

    # Always write to local storage
    write_csv(data, local_output_dir)

    # Try to write to USB drive
    usb_mount = find_usb_drive()
    if usb_mount:
        try:
            usb_output_dir = os.path.join(usb_mount, 'temperature_logs')
            write_csv(data, usb_output_dir)
            logging.info("Data successfully written to USB drive")
        except Exception as e:
            logging.error(f"Error writing to USB drive: {str(e)}")
    else:
        logging.warning("No USB drive found. Data only saved locally.")

if __name__ == "__main__":
    logging.info("Script started")
    main()
    logging.info("Script completed")
