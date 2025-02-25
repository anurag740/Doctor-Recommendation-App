from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

def scrape_doctors(specialty, location):
    search_query = f"{specialty} doctors in {location}"
    url = f"https://www.google.com/search?q={search_query}"
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    
    time.sleep(3)  # Allow time for the page to load
    
    doctor_results = []
    results = driver.find_elements(By.CSS_SELECTOR, ".tF2Cxc")  # Google search result containers
    
    for result in results[:10]:  # Limiting to top 10 results
        try:
            name = result.find_element(By.CSS_SELECTOR, "h3").text
            link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            snippet = result.find_element(By.CSS_SELECTOR, ".VwiC3b").text  # Short description
            
            doctor_results.append({
                "name": name,
                "rating": snippet,  # Assuming rating info may be in snippet
                "profile_link": link
            })
        except Exception as e:
            continue
    
    driver.quit()
    return doctor_results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    specialty = request.form['specialty']
    location = request.form['location']
    
    doctors = scrape_doctors(specialty, location)
    return render_template('results.html', doctors=doctors)

if __name__ == '__main__':
    app.run(debug=True)
