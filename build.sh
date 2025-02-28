#!/bin/bash

echo "Installing Google Chrome..."
curl -o /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i /tmp/chrome.deb || sudo apt-get -f install -y

echo "Installing ChromeDriver..."
curl -Lo /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.111/linux64/chromedriver-linux64.zip
unzip /tmp/chromedriver.zip -d /tmp
sudo mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver

echo "Chrome and ChromeDriver installation complete!"
