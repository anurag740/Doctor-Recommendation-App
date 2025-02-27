import os  
import subprocess
import logging
import time
import random
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Install Chrome & ChromeDriver on Render
if "RENDER" in os.environ:
    logging.info("Installing Chrome and ChromeDriver on Render...")

    # Install Google Chrome
    subprocess.run("wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -", shell=True)
    subprocess.run("sudo apt-get update", shell=True)
    subprocess.run("sudo apt-get install -y google-chrome-stable", shell=True)

    # Install ChromeDriver
    subprocess.run("curl -Lo /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.111/linux64/chromedriver-linux64.zip", shell=True)
    subprocess.run("unzip /tmp/chromedriver.zip -d /tmp", shell=True)
    subprocess.run("sudo mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver", shell=True)
    subprocess.run("sudo chmod +x /usr/bin/chromedriver", shell=True)

    os.environ["GOOGLE_CHROME_BIN"] = "/usr/bin/google-chrome"
    os.environ["CHROMEDRIVER_PATH"] = "/usr/bin/chromedriver"

app = Flask(__name__)

# Set ChromeDriver Path
CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

def scrape_doctors(specialty, location):
    """Scrape Google for doctors based on specialty and location."""
    search_query = f"{specialty} doctors in {location}"
    google_url = f"https://www.google.com/search?q={search_query}&tbm=lcl"

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    if "RENDER" in os.environ:
        options.binary_location = os.environ["GOOGLE_CHROME_BIN"]

    logging.info(f"Using ChromeDriver path: {CHROMEDRIVER_PATH}")
    
    # Check if ChromeDriver exists
    if not os.path.exists(CHROMEDRIVER_PATH):
        logging.error(f"ChromeDriver not found at path: {CHROMEDRIVER_PATH}")
        return []

    try:
        logging.info("Launching Chrome WebDriver...")
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(google_url)
        time.sleep(random.uniform(3, 6))

        # Click "More places" button if available
        try:
            more_button = driver.find_element(By.CSS_SELECTOR, "g-more-link a")
            driver.execute_script("arguments[0].click();", more_button)
            time.sleep(random.uniform(3, 5))
        except:
            try:
                more_button = driver.find_element(By.CSS_SELECTOR, "div[jsname='c1gLCb'] span.LGwnxb")
                driver.execute_script("arguments[0].click();", more_button)
                time.sleep(random.uniform(3, 5))
            except:
                logging.info("No 'More places' button found.")

        results = []
        doctor_containers = driver.find_elements(By.CSS_SELECTOR, "div[jsname='MZArnb']")

        for container in doctor_containers[:20]:  # Get up to 20 results
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

        logging.info(f"Scraped {len(results)} doctors successfully.")
        return results

    except Exception as e:
        logging.error(f"Error during scraping: {e}", exc_info=True)
        return []

    finally:
        driver.quit()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    """Handles the doctor recommendation request."""
    try:
        specialty = request.form["specialty"]
        location = request.form["location"]
        logging.info(f"User requested doctors for: {specialty} in {location}")

        doctors = scrape_doctors(specialty, location)

        if not doctors:
            logging.warning("No doctors found or scraping failed.")

        return render_template("results.html", doctors=doctors)

    except Exception as e:
        logging.error(f"Internal Server Error: {e}", exc_info=True)
        return f"Internal Server Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
