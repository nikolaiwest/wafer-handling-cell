# Raspberry Pi Sense HAT Data Collection and Server Logging System

This project is designed to facilitate the collection of sensor data from Raspberry Pi units equipped with Sense HATs and to aggregate this data on a central server. The system consists of two main scripts (`sender.py` and `server.py`), and their respective launchers (`launch_sender.py` and `launch_server.py`), making it easy to deploy and manage both the data collection and aggregation processes.

## Project Description

- `server.py` sets up a server to listen for incoming sensor data from multiple Raspberry Pi units, logging the received data into a structured CSV file for later analysis.
- `sender.py`, intended for deployment on Raspberry Pi units with Sense HATs, gathers various sensor data and sends it to the server.

### Requirements

#### Hardware:
- Raspberry Pi 3B units with Sense HAT attachments for collecting sensor data.
- A server capable of running Python and handling TCP/IP connections to aggregate the data.

#### Software:
- Python 3.11.2 installed on both the Raspberry Pi units and the server.
- The `sense-hat` Python library installed on the Raspberry Pi units.
- Standard Python libraries (`socket`, `csv`, `os`, `json`, `datetime`) are used within the scripts.

## Installation

1. Ensure Python 3.11.2 is installed on your Raspberry Pi units and server.
2. Clone this repository onto both your Raspberry Pi units and the server.
3. Install the `sense-hat` library on the Raspberry Pi units using pip:

    pip3 install sense-hat

4. Configure the server IP and port in the `server.json` file located at `/home/rpi01/adept` (adjust `rpi01` to match your Raspberry Pi unit names) and ensure the server's IP and port allow connections from your Raspberry Pi units.

## Usage

### On the Server

Run the `launch_server.py` script to start listening for incoming data:

    python3 launch_server.py


The server will automatically create or append to the `whc_data.csv` file, logging all received sensor data.

### On Raspberry Pi Units

Execute the `launch_sender.py` script to begin collecting and transmitting sensor data to the server:

    python3 launch_sender.py

The script will continuously send sensor data at the configured frequency to the server.

## Customization

Adjust the list of allowed IP addresses in the `server.py` script to include only your Raspberry Pi units. You may also modify the data sending frequency in the `sender.py` script according to your requirements.

## License

This project is distributed under the MIT License. See the LICENSE file for more details.

## Disclaimer

This software is provided "as is", without warranty of any kind. Use it at your own risk.