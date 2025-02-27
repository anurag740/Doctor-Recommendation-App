import os  
import subprocess
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random

# Install Chrome in Render Deployment Environment
if "RENDER" in os.environ:
    subprocess.run("curl -o /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", shell=True)
    subprocess.run("sudo dpkg -i /tmp/chrome.deb; sudo apt-get -f install -y", shell=True)
    os.environ["GOOGLE_CHROME_BIN"] = "/usr/bin/google-chrome"

app = Flask(__name__)

# Set ChromeDriver Path for Render
CHROMEDRIVER_PATH = "/usr/bin/chromedriver" if "RENDER" in os.environ else "C:/Users/LENOVO/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"

def scrape_doctors(specialty, location):
    search_query = f"{specialty} doctors in {location}"
    google_url = f"https://www.google.com/search?q={search_query}&tbm=lcl"

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    if "RENDER" in os.environ:
        options.binary_location = "/usr/bin/google-chrome"

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
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
