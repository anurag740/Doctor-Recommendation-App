import os
import platform
import subprocess
import chromedriver_autoinstaller
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths
IS_WINDOWS = platform.system() == "Windows"
CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe" if IS_WINDOWS else "/opt/render/.local/bin/google-chrome"
CHROMEDRIVER_PATH = chromedriver_autoinstaller.install()

def install_chrome():
    """Installs Chrome only if running on Render (Linux). Skips on Windows."""
    if IS_WINDOWS:
        logger.info("Skipping Chrome installation on Windows.")
        return

    if not os.path.exists(CHROME_PATH):
        logger.info("Installing Google Chrome...")
        subprocess.run(
            "wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb && "
            "dpkg -x /tmp/chrome.deb /tmp/chrome && "
            "mkdir -p /opt/render/.local/bin && "
            "mv /tmp/chrome/opt/google/chrome/google-chrome /opt/render/.local/bin/google-chrome",
            shell=True,
            check=True
        )
        logger.info("Google Chrome installed successfully.")

install_chrome()

app = Flask(__name__)

def scrape_doctors(specialty, location):
    search_query = f"{specialty} doctors in {location}"
    google_url = f"https://www.google.com/search?q={search_query}&tbm=lcl"

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    if not IS_WINDOWS:
        options.binary_location = CHROME_PATH

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(google_url)
        time.sleep(random.uniform(3, 6))

        results = []
        doctor_containers = driver.find_elements(By.CSS_SELECTOR, "div[jsname='MZArnb']")

        for container in doctor_containers[:20]:
            try:
                name = container.find_element(By.CSS_SELECTOR, "div.dbg0pd span.OSrXXb").text
            except:
                name = "Not Available"

            try:
                rating = container.find_element(By.CSS_SELECTOR, "span.yi40Hd").text
            except:
                rating = "No Rating"

            try:
                review_count = container.find_element(By.CSS_SELECTOR, "span.RDApEe").text.strip("()")
            except:
                review_count = "No Reviews"

            try:
                address = container.find_elements(By.CSS_SELECTOR, "div")[2].text
            except:
                address = "No Address"

            try:
                status = container.find_elements(By.CSS_SELECTOR, "div")[3].text
            except:
                status = "Unknown"

            results.append({
                "name": name,
                "rating": rating,
                "reviews": review_count,
                "address": address,
                "status": status,
            })

        return results

    finally:
        driver.quit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    specialty = request.form["specialty"]
    location = request.form["location"]
    doctors = scrape_doctors(specialty, location)
    return render_template("results.html", doctors=doctors)

if __name__ == "__main__":
    app.run(debug=True)
