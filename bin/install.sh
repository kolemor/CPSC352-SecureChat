#!/bin/bash

# Update package lists
sudo apt update

# *************************************

# Install HTTPie for Terminal to work with REST APIs
sudo apt install -y httpie

# Install pip for Python 3
sudo apt install -y python3-pip

# Install required libaries for the project
pip3 install -r Requirements.txt