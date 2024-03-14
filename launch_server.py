"""
Script Name: launch_server.py
Author: Nikolai West 
Date Created: 14.03.2024
Last Modified: 14.03.2024
Version: 1.0.0
"""

from server import Server


def main():
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
