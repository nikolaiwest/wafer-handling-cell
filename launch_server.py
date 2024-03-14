"""
Script Name: launch_server.py
Author: Nikolai West
Date Created: 14.03.2024
Last Modified: 14.03.2024
Version: 1.0.2
"""

# default
import logging

# project
from server import Server


def configure_logging():
    """Configures the global logging level and format, and sets up file and console handlers."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the global logging level

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler for outputting logs to a file
    file_handler = logging.FileHandler("server.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler for outputting logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def main():
    configure_logging()  # Configure logging before starting the server
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
