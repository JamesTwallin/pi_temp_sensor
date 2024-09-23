# Raspberry Pi Temperature Sensor Logger

This project uses a Raspberry Pi with a DS18B20 temperature sensor to log temperature readings. The readings are stored as individual JSON files on an attached USB stick.

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- DS18B20 temperature sensor
- USB stick for data storage

## Software Requirements

- Raspberry Pi OS (formerly Raspbian)
- Python 3
- Required Python libraries: `os`, `glob`, `time`, `json`, `datetime`

## Setup

1. Connect the DS18B20 sensor to your Raspberry Pi:
   - VCC to 3.3V
   - GND to Ground
   - DATA to GPIO 4 (Pin 7)

2. Enable the 1-Wire interface:
   ```
   sudo nano /boot/config.txt
   ```
   Add the following line at the end of the file:
   ```
   dtoverlay=w1-gpio
   ```
   Save and reboot your Raspberry Pi.

3. Clone this repository:
   ```
   git clone https://github.com/JamesTwallin/pi_temp_sensor.git
   cd pi_temp_sensor
   ```

4. Install the required Python libraries (if not already installed):
   ```
   pip3 install -r requirements.txt
   ```

5. Plug in your USB stick and note its mount point (e.g., `/media/pi/USB_STICK`)

6. Update the `USB_MOUNT_POINT` variable in the `temp_sensor.py` script with your USB stick's mount point.

## Usage

Run the script manually:

```
python3 temp_sensor.py
```

The script will create JSON files with temperature readings on the USB stick.

## Running on Boot
### Service file
```
[Unit]
Description=Temperature Sensor Logger
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/temp_sensor.py
WorkingDirectory=/home/pi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```


To run the script automatically on boot:

1. Copy the systemd service file to the appropriate directory:
   ```
   sudo cp temp_sensor.service /etc/systemd/system/
   ```

2. Enable and start the service:
   ```
   sudo systemctl enable temp_sensor.service
   sudo systemctl start temp_sensor.service
   ```

## Troubleshooting

- If the sensor is not detected, check your wiring and ensure the 1-Wire interface is enabled.
- If data is not being written to the USB stick, check that it's properly mounted and the mount point in the script is correct.
- View service logs with: `sudo journalctl -u temp_sensor.service`

## License

This project is licensed under the MIT License
