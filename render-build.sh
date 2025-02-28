#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Installing Google Chrome..."
wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get update && apt-get install -y /tmp/chrome.deb

echo "Installing ChromeDriver..."
wget -q -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/120.0.6099.109/linux64/chromedriver-linux64.zip
unzip /tmp/chromedriver.zip -d /tmp/chromedriver-linux64/
chmod +x /tmp/chromedriver-linux64/chromedriver

echo "Setup completed successfully!"
