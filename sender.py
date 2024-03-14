"""
Script Name: sender.py
Author: Nikolai West 
Date Created: 13.03.2024
Last Modified: 13.03.2024
Version: 1.0.0
"""

# default
import json
import time
import socket
import itertools
from datetime import datetime

# other
from sense_hat import SenseHat


class Sender:
    """Handles data collection from the Sense HAT and transmission to a server."""

    def __init__(self):
        """Initializes the sender with server credentials and sense hat setup."""
        # Identifier for the Raspberry Pi
        self.name = "rpi01"
        # Load server credentials from a file
        self.set_server_creds()
        # Initialize the Sense HAT
        self.sense_hat = SenseHat()
        # Placeholder for the socket connection
        self.sock: socket = None
        # Current count of reconnection attempts
        self.cur_recon_attempts: int = 0
        # Maximum allowed reconnection attempts
        self.max_recon_attempts: int = 100
        # Iterators for LED index and update frequency
        self.iter_led_idx = itertools.cycle(range(8))
        self.iter_led_upd = itertools.cycle(range(10))

    def fetch_data(self) -> str:
        """Collects sensor data from the Sense HAT and formats it as a string."""
        # Orientation in degree(0-360°) using aircraft axes (roll, pitch, yaw)
        ori = self.sense_hat.get_orientation_degrees()
        ori_str = f'{ori["roll"]},{ori["pitch"]},{ori["yaw"]},'
        # Raw gyroscope data in radians per second (x, y, z)
        gyr = self.sense_hat.get_gyroscope_raw()
        gyr_str = f'{gyr["x"]},{gyr["y"]},{gyr["z"]},'
        # Raw accelerometer data in Gs (x, y, z)
        acc = self.sense_hat.get_accelerometer_raw()
        acc_str = f'{acc["x"]},{acc["y"]},{acc["z"]}'
        # Get time after fetching as timestamp
        time_str = datetime.now().strftime("%H:%M:%S.%f")
        # Format and return the data as a string
        return f"{time_str},{self.name},{ori_str}{gyr_str}{acc_str}"

    def send_data(self):
        """Sends the collected data to the server via TCP."""
        # Fetch the sensor data
        data = self.fetch_data()
        # Establish a connection if not already connected
        if not self.sock:
            self.reconnect()
        # Send data
        try:
            # Attempt to send data
            self.sock.sendall(data.encode("utf-8"))
        # Handle potential sending errors
        except socket.error as e:
            print(f"Attempting to reconnect after connection error: {e}.")
            self.reconnect()
            try:
                self.sock.sendall(data.encode("utf-8"))
            except socket.error as e:
                print(f"Failed to send data after reconnecting: {e}")

    def reconnect(self):
        """Attempts to reconnect to the server with exponential backoff."""
        if self.sock:
            try:
                # Ensure the current socket is closed before retrying
                self.sock.close()
            except socket.error as e:
                print(f"Error closing socket: {e}")
            finally:
                self.sock = None

        # Exponential backoff sequence for reconnection attempts
        reconnect_wait_times = [1, 2, 4, 8, 16, 32]

        # Start an indefinite loop for reconnection attempts
        while True:
            if (
                self.max_recon_attempts is not None
                and self.cur_recon_attempts >= self.max_recon_attempts
            ):
                print(f"Failed to reconnect after {self.max_recon_attempts} attempts.")
                # Stop trying after reaching the max number of attempts
                self.sense_hat.show_letter("X", text_colour=(255, 0, 0))  # aborted
                break

            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.server_ip, self.server_port))
                print("Successfully reconnected to the server.")
                # Reset the counter after a successful connection
                self.cur_recon_attempts = 0
                # Exit the loop upon successful connection
                return
            except socket.error as e:
                # Connection failed
                print(f"Failed to connect to server: {e}")
                self.sock = None
                self.cur_recon_attempts += 1
                # Update the LED to indicate a retry
                self.update_led_pb("r")

                # Set a wait time based on reconnection attepts
                if self.max_recon_attempts is None:
                    wait_time = (
                        reconnect_wait_times[-1]
                        if self.cur_recon_attempts > len(reconnect_wait_times)
                        else min(60, 2 ** (self.cur_recon_attempts - 1))
                    )
                else:
                    wait_time_index = min(
                        self.cur_recon_attempts - 1, len(reconnect_wait_times) - 1
                    )
                    wait_time = min(reconnect_wait_times[wait_time_index], 60)
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)

    def set_led_number(self):
        """Displays the Raspberry Pi's identifier number on the Sense HAT's LED matrix."""
        pixel_path = f"/home/{self.name}/wafer_handling_cell/numbers.json"
        pixel_list = self.load_json(pixel_path)[self.name]
        self.sense_hat.set_pixels(pixel_list)

    def update_led_pb(self, color: str = "b"):
        """Updates the LED matrix to visually indicate the script's progress and status."""
        idx_next = next(self.iter_led_idx)
        idx_last = 7 if idx_next == 0 else idx_next - 1
        # Reset the last pixel
        self.sense_hat.set_pixel(0, idx_last, (0, 0, 0))
        # Set current pixel according to selected color
        col_next = (
            (255, 0, 0)
            if color == "r"
            else (0, 255, 0) if color == "g" else (0, 0, 255)
        )
        self.sense_hat.set_pixel(0, idx_next, col_next)

    def run(self):
        """Main loop to continuously send sensor data to the server."""
        # Display the Pi's identifier on startup
        self.set_led_number()

        while True:
            try:
                # Send data to the server
                self.send_data()
                # Update the LED matrix periodically to indicate successful data sends
                if next(self.iter_led_upd) == 0:
                    self.update_led_pb("g")
            except KeyboardInterrupt:
                print("Sender stopped by user.")
                self.sense_hat.show_letter("A", text_colour=(0, 0, 255))  # aborted
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                self.reconnect()

    def load_json(self, path: str) -> dict:
        """Loads JSON data from a file, returning it as a dictionary."""
        try:
            with open(path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"File not found: {path}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON file provided: {e}")
        # Return None or an empty dict if loading fails.
        return None

    def set_server_creds(self) -> None:
        """Sets the server IP and port based on the loaded server credentials."""
        path = f"/home/{self.name}/wafer_handling_cell/server.json"
        credentials = self.load_json(path)
        if credentials is None:
            raise ValueError(f"Credentials could not be loaded: {path}")
        self.server_ip = credentials.get("ip", "")
        self.server_port = credentials.get("port", 0)
