import os
import glob
import time
import csv
from datetime import datetime, timezone

# Initialize the 1-Wire interface
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Define the directory where the sensor data is stored
base_dir = '/sys/bus/w1/devices/'

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

def main():
    device_file = find_device()
    if not device_file:
        print("Error: DS18B20 sensor not found. Please check your connections and ensure the sensor is properly set up.")
        return

    print("DS18B20 sensor found. Starting temperature readings...")

    # Create a directory for CSV files if it doesn't exist
    csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temperature_logs')
    os.makedirs(csv_dir, exist_ok=True)

    # Create a new CSV file with current timestamp
    csv_filename = os.path.join(csv_dir, f'temperature_log_{get_zulu_timestamp()}.csv')
    
    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Timestamp', 'Temperature (°C)', 'Temperature (°F)'])

        try:
            while True:
                celsius, fahrenheit = read_temp(device_file)
                timestamp = get_zulu_timestamp()
                
                if celsius is not None and fahrenheit is not None:
                    print(f"{timestamp} - Temperature: {celsius:.1f}°C | {fahrenheit:.1f}°F")
                    csv_writer.writerow([timestamp, f"{celsius:.1f}", f"{fahrenheit:.1f}"])
                    csvfile.flush()  # Ensure data is written to the file immediately
                else:
                    print(f"{timestamp} - Error reading temperature. Retrying...")
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("Script terminated by user.")
            print(f"Data saved to {csv_filename}")

if __name__ == "__main__":
    main()
