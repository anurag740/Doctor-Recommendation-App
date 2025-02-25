from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the cleaned dataset
doctors_df = pd.read_excel("D:/git_projects/Doctor-Recommendation-App/data/cleaned_doctor_data.xlsx", sheet_name="Doctors")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    specialty = request.form.get('specialty', '').lower()
    location = request.form.get('location', '').lower()
    
    # Filter doctors based on user input
    filtered_doctors = doctors_df[
        (doctors_df['specialties'].str.lower().str.contains(specialty, na=False)) &
        ((doctors_df['city'].str.lower() == location) | (doctors_df['country'].str.lower() == location))
    ]
    
    return render_template('results.html', doctors=filtered_doctors.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)