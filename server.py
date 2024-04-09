"""
Script Name: server.py
Author: Nikolai West 
Date Created: 14.03.2024
Last Modified: 09.04.2024
Version: 1.0.3
"""

# default
import os
import csv
import json
import socket
import logging
import threading


class Server:
    """A server class for receiving data from specific IP addresses and saving it to a CSV file."""

    def __init__(self):
        """Initializes the server with predefined settings."""
        # Get a logger for this module
        self.logger = logging.getLogger(__name__)
        # Name of the server, used for identifying configuration files
        self.set_name()
        # Set the server IP and port from a configuration file
        self.set_server_creds()
        # Initialize the output file
        self.set_output_csv()
        # Creates a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allows the socket to reuse the address
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # List of IP addresses allowed to connect to this server
        self.allowed_ips = [
            "192.168.0.201",
            "192.168.0.202",
            "192.168.0.203",
            "192.168.0.204",
        ]

    def listen(self):
        """Listens for incoming connections and handles them if they are from allowed IPs."""
        # Bind the socket to the configured IP and port
        self.sock.bind((self.server_ip, self.server_port))
        # Listen for connections, queueing up to 5 connection requests
        self.sock.listen(5)
        self.logger.info(f"Server listening on {self.server_ip}:{self.server_port}")

        while True:
            # Accept a new connection
            client, address = self.sock.accept()
            ip_address = address[0]
            # Checks if the IP address is allowed
            if ip_address in self.allowed_ips:
                # Create a new thread for each client connection
                client_thread = threading.Thread(
                    target=self.handle_client, args=(client,)
                )
                client_thread.start()  # Start the thread
            else:
                self.logger.warning(
                    f"Connection attempt from unauthorized IP address: {ip_address}"
                )
                client.close()

    def handle_client(self, client_socket):
        """Receives data from a client and continuously saves it until the connection is closed."""
        try:
            while True:
                # Attempt to receive data from the client
                message = client_socket.recv(1024).decode("utf-8")
                # Break the loop if no data is received, indicating the client has closed the connection
                if not message:
                    break
                # Save the received data
                self.save_data(message)
        except socket.error as e:
            self.logger.error(f"Socket error: {e}")
        finally:
            # Close the connection once done
            client_socket.close()

    def save_data(self, data):
        """Saves the received data along with a timestamp to the CSV file."""
        # Split the received data string into parts
        parts = data.split(",")

        # Write the data row
        with open(self.csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(parts)

    def run(self):
        """Runs the server, handling graceful shutdown and errors."""
        try:
            self.listen()
        except KeyboardInterrupt:
            self.logger.info("Server shutting down.")
        except Exception as e:
            self.logger.exception("An error occurred: ", exc_info=e)
        finally:
            # Ensures the socket is closed on shutdown or error
            self.sock.close()

    def load_json(self, path: str) -> dict:
        """Loads JSON data from a file, returning it as a dictionary."""
        try:
            with open(path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.error(f"File not found: {path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON file provided: {e}", exc_info=e)
        # Returns None if loading fails
        return None

    def set_name(self) -> None:
        cur_path = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(cur_path)
        self.name = os.path.basename(parent_dir)

    def set_server_creds(self) -> None:
        """Sets the server's IP and port from a configuration file."""
        # Path to the configuration file
        path = f"/home/{self.name}/wafer-handling-cell/server.json"
        credentials = self.load_json(path)
        if credentials is None:
            raise ValueError(f"Credentials could not be loaded: {path}")
        self.server_ip = credentials.get("ip", "")
        self.server_port = credentials.get("port", 0)

    def set_output_csv(self) -> None:
        """
        Initializes the CSV output file for data logging.
        If the file doesn't exist, it creates it and adds the header row.
        """
        # The CSV file where data will be saved
        self.csv_path = f"/home/{self.name}/wafer-handling-cell/whc_data.csv"

        # Define column headers for the CSV file
        headers = [
            "time",
            "sh_id",
            "ori_r",
            "ori_p",
            "ori_y",
            "gyr_x",
            "gyr_y",
            "gyr_z",
            "acc_x",
            "acc_y",
            "acc_z",
        ]

        # Check if the CSV file already exists and has a header
        file_exists = os.path.isfile(self.csv_path)

        with open(self.csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            # If the file doesn't exist, write the header first
            if not file_exists:
                writer.writerow(headers)
