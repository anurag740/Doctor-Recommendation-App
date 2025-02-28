# 🏥 Doctor Recommendation Web App

## 📌 Overview
The **Doctor Recommendation Web App** helps users find doctors based on their specialty and location. It scrapes Google search results to fetch relevant doctor details such as name, rating, reviews, and address.

## 🚀 Features
- Search for doctors based on **specialty** and **location**
- **Live web scraping** using Selenium to fetch doctor details
- **Flask-powered web app** with an interactive UI
- **Deployable on Render** for easy hosting

## 🛠️ Tech Stack
- **Backend:** Flask, Selenium
- **Frontend:** HTML, CSS (Flask Templates)
- **Web Scraping:** Selenium with ChromeDriver
- **Deployment:** Render

## 🔧 Setup & Installation
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/doctor-recommendation-app.git
cd doctor-recommendation-app
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate    # For Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Create a `.env` file and add:
```
RENDER=true
GOOGLE_CHROME_BIN=/usr/bin/google-chrome
CHROMEDRIVER_PATH=/tmp/chromedriver-linux64/chromedriver
```

### 5️⃣ Run the Application Locally
```bash
flask run
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## 🌍 Deployment on Render
1. Push the code to **GitHub**
2. Connect the repository to **Render.com**
3. Add a **Build Command**: `./render-build.sh && pip install -r requirements.txt`
4. Set **Environment Variables** as shown above
5. Deploy and access the live app!

## 📜 Render Build Script (render-build.sh)
Create a `render-build.sh` file:
```bash
#!/bin/bash

# Install Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
dpkg --configure -a
sudo apt update && sudo apt install -y google-chrome-stable

# Install ChromeDriver
CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P /tmp/
unzip /tmp/chromedriver_linux64.zip -d /tmp/
chmod +x /tmp/chromedriver
```

## 🔍 How It Works
1. User enters a **specialty** (e.g., "Cardiologist") and **location** (e.g., "New York").
2. The app performs a **Google search** and scrapes doctor details.
3. Results are displayed with **name, rating, reviews, and address**.

## 🛠️ Troubleshooting
### **Selenium WebDriver Issues**
- Ensure **Google Chrome** and **ChromeDriver** versions match.
- Run in **headless mode** if deploying remotely.

### **Render Deployment Errors**
- Check logs for missing **dependencies**.
- Ensure environment variables are **correctly set**.

## 📜 License
This project is licensed under the **MIT License**.

## 🤝 Contributing
Feel free to fork the repo, make changes, and submit a **pull request**! 🚀

