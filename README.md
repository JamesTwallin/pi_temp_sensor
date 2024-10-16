# Raspberry Pi Temperature Sensor Logger

This project uses a Raspberry Pi with a DS18B20 temperature sensor to log temperature readings. The readings are stored as hourly CSV files both locally and on an attached USB stick (if available).

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- DS18B20 temperature sensor
- USB stick for redundant data storage (optional)

## Software Requirements

- Raspberry Pi OS (formerly Raspbian)
- Python 3
- Required Python libraries: `os`, `glob`, `csv`, `datetime`

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

5. (Optional) Plug in your USB stick. The script will automatically detect and use it if available.

## Usage

The script is designed to run every minute via a cron job. To set this up:

1. Open the crontab file:
   ```
   crontab -e
   ```

2. Add the following line:
   ```
   * * * * * /usr/bin/python3 /home/pi/pi_temp_sensor/temp_sensor.py >> /home/pi/temp_sensor.log 2>&1
   ```

3. Save and exit (in nano, press Ctrl+X, then Y, then Enter).

The script will create hourly CSV files with temperature readings both locally and on the USB stick (if available).

## Output

- CSV files are created in the format: `YYYY-MM-DDTHH.csv`
- Each file contains readings for one hour
- Files are stored in `/home/pi/Desktop/temperature_logs/` and on the USB drive (if available)

## Troubleshooting

- If the sensor is not detected, check your wiring and ensure the 1-Wire interface is enabled.
- If data is not being written to the USB stick, check that it's properly mounted.
- Check `/home/pi/temp_sensor.log` for any error messages.
- Ensure the DS18B20 sensor is properly connected to the GPIO pins.
- Verify that the 1-Wire interface is enabled in raspi-config.

## Maintenance

- Regularly check available storage space, especially if using a USB drive with limited capacity.
- Consider implementing a log rotation system for long-term use to manage file sizes.

## License

This project is licensed under the MIT License.
