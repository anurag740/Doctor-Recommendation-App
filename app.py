import os  
import subprocess
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random

app = Flask(__name__)


if "RENDER" in os.environ:
    CHROMEDRIVER_PATH = "/tmp/chromedriver-linux64/chromedriver-linux64/chromedriver"  
    CHROME_BINARY_PATH = os.environ.get("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome")
else:
    CHROMEDRIVER_PATH = "C:/Users/LENOVO/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
    CHROME_BINARY_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"

def scrape_doctors(specialty, location):
    search_query = f"{specialty} doctors in {location}"
    google_url = f"https://www.google.com/search?q={search_query}&tbm=lcl"

    options = Options()
    options.binary_location = CHROME_BINARY_PATH  # Set Chrome binary location
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)


    try:
        driver.get(google_url)
        time.sleep(random.uniform(3, 6))

        # 🔍 Click "More places" button if available
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
                print("No 'More places' button found.")

        results = []
        doctor_containers = driver.find_elements(By.CSS_SELECTOR, "div[jsname='MZArnb']")

        for container in doctor_containers[:20]:  # Get up to 10 results
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
        print("Error:", e)
        return []

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
