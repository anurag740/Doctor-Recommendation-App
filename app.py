import os
import chromedriver_autoinstaller
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Chrome & Chromedriver paths for Render
if "RENDER" in os.environ:
    os.environ["GOOGLE_CHROME_BIN"] = "/opt/render/.local/bin/google-chrome-stable"
    os.environ["CHROMEDRIVER_BIN"] = "/opt/render/.local/bin/chromedriver"

# Ensure ChromeDriver is installed
chromedriver_autoinstaller.install()

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

    if "RENDER" in os.environ:
        options.binary_location = os.environ["GOOGLE_CHROME_BIN"]

    driver = None
    try:
        service = None
        if "RENDER" in os.environ:
            service = webdriver.ChromeService(executable_path=os.environ["CHROMEDRIVER_BIN"])

        driver = webdriver.Chrome(service=service, options=options)
        logger.info("ChromeDriver started successfully.")

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
        if driver:
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
        if not doctors:
            logger.warning("No doctors found or scraping failed.")
        return render_template("results.html", doctors=doctors)
    except Exception as e:
        logger.error(f"Internal Server Error: {e}")
        return f"Internal Server Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
