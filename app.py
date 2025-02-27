import os
import time
import random
import logging
import subprocess
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Manually set Chrome & Chromedriver paths for Render
CHROME_PATH = "/opt/render/.local/bin/google-chrome-stable"
CHROMEDRIVER_PATH = "/opt/render/.local/bin/chromedriver"

# Check if running on Render
ON_RENDER = "RENDER" in os.environ

# Ensure Chrome & Chromedriver exist
if ON_RENDER:
    if not os.path.exists(CHROME_PATH):
        raise ValueError("Google Chrome not found at expected path.")
    if not os.path.exists(CHROMEDRIVER_PATH):
        raise ValueError("Chromedriver not found at expected path.")

app = Flask(__name__)

def scrape_doctors(specialty, location):
    search_query = f"{specialty} doctors in {location}"
    google_url = f"https://www.google.com/search?q={search_query}&tbm=lcl"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Set Chrome binary location
    if ON_RENDER:
        options.binary_location = CHROME_PATH

    # Setup Chrome WebDriver
    service = Service(CHROMEDRIVER_PATH) if ON_RENDER else None
    driver = webdriver.Chrome(service=service, options=options)

    try:
        logger.info("Opening Google search results...")
        driver.get(google_url)
        time.sleep(random.uniform(3, 6))

        # Try clicking "More places" button if available
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
                logger.info("No 'More places' button found.")

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

    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return []

    finally:
        driver.quit()
        logger.info("ChromeDriver closed.")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        specialty = request.form["specialty"]
        location = request.form["location"]
        doctors = scrape_doctors(specialty, location)
        return render_template("results.html", doctors=doctors)
    except Exception as e:
        logger.error(f"Internal Server Error: {e}")
        return f"Internal Server Error: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
