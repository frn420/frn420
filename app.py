from flask import Flask, render_template, request, url_for, redirect, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
from food_predictor import predict_nutrients

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('homepage.html')  # Serve the homepage

@app.route('/signup.html')
def signup():
    return render_template('signup.html')  # Serve signup.html

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Perform login logic here
        return redirect(url_for('home'))  # Redirect to the homepage after login
    return render_template('login.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Handle file upload
        file = request.files['food_image']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Perform prediction
        food_name, nutrients = predict_nutrients(filepath)
        image_url = url_for('static', filename=f'uploads/{filename}')

        # Prepare result
        result = {
            'food': food_name,
            'nutrients': nutrients,
            'image_url': image_url
        }
        return render_template('dashboard.html', result=result)  # Show results on the dashboard
    except Exception as e:
        return render_template('dashboard.html', error=str(e))  # Show error on the dashboard

if __name__ == '__main__':
    app.run(debug=True)
