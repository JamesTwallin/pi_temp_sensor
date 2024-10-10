import os
import glob
import time
import csv
from datetime import datetime, timezone
from io import StringIO

# Initialize the 1-Wire interface
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Define the directory where the sensor data is stored
base_dir = '/sys/bus/w1/devices/'

# Desktop path for the pi user
DESKTOP_PATH = '/home/pi/Desktop'

# Buffer size and write interval
BUFFER_SIZE = 60  # Number of readings to buffer before writing
WRITE_INTERVAL = 60  # Seconds between writes

def find_device():
    device_folders = glob.glob(base_dir + '28*')
    return device_folders[0] + '/w1_slave' if device_folders else None

def read_temp_raw(device_file):
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temp(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        return float(temp_string) / 1000.0
    return None

def get_zulu_timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def create_csv(start_time):
    day_folder = os.path.join(DESKTOP_PATH, 'temperature_logs', start_time[:10])  # YYYY-MM-DD
    try:
        os.makedirs(day_folder, exist_ok=True)
        
        csv_filename = f"{start_time.replace(':', '')}.csv"
        csv_path = os.path.join(day_folder, csv_filename)
        
        with open(csv_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Timestamp", "Temperature (°C)"])
        
        return csv_path
    except IOError as e:
        print(f"Error creating CSV file: {e}")
        return None

def write_buffer_to_csv(csv_path, buffer):
    try:
        with open(csv_path, 'a', newline='') as csvfile:
            csvfile.write(buffer.getvalue())
        buffer.truncate(0)
        buffer.seek(0)
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

def main():
    device_file = find_device()
    if not device_file:
        print("Error: DS18B20 sensor not found. Please check your connections and ensure the sensor is properly set up.")
        return
    print("DS18B20 sensor found. Starting temperature readings...")
    
    start_time = get_zulu_timestamp()
    csv_path = create_csv(start_time)
    if csv_path is None:
        print("Failed to create CSV file. Exiting.")
        return

    buffer = StringIO()
    csv_writer = csv.writer(buffer)
    
    readings_count = 0
    last_write_time = time.time()
    
    try:
        while True:
            celsius = read_temp(device_file)
            timestamp = get_zulu_timestamp()
            
            if celsius is not None:
                csv_writer.writerow([timestamp, f"{celsius:.1f}"])
                print(f"{timestamp} - Temperature: {celsius:.1f}°C")
                readings_count += 1
            else:
                print(f"{timestamp} - Error reading temperature. Retrying...")
            
            current_time = time.time()
            if readings_count >= BUFFER_SIZE or (current_time - last_write_time) >= WRITE_INTERVAL:
                write_buffer_to_csv(csv_path, buffer)
                readings_count = 0
                last_write_time = current_time
            
            time.sleep(30)
    except KeyboardInterrupt:
        print("Script terminated by user.")
        write_buffer_to_csv(csv_path, buffer)  # Write any remaining data
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        write_buffer_to_csv(csv_path, buffer)  # Attempt to write data on error

if __name__ == "__main__":
    main()
