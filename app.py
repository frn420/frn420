from flask import Flask, render_template, request, url_for, redirect, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
from food_predictor import predict_nutrients

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
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

@app.route('/food-predictor', methods=['GET', 'POST'])
def food_predictor():
    if request.method == 'POST':
        # Handle file upload and prediction logic
        if 'food_image' not in request.files:
            return "No file part", 400

        file = request.files['food_image']
        if file.filename == '':
            return "No selected file", 400

        if file:
            # Save the uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Call the food predictor function
            food_name, nutrients = predict_nutrients(filepath)

            # Render the results in a template
            return render_template(
                'food_predictor.html',
                result={
                    'image_url': url_for('static', filename=f'uploads/{filename}'),
                    'food': food_name,
                    'nutrients': nutrients,
                    'message': f"Your {food_name} is ready for donation!"
                }
            )
    return render_template('food_predictor.html')  # For GET requests

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'imageUpload' not in request.files:
        return "No file part", 400

    file = request.files['imageUpload']
    if file.filename == '':
        return "No selected file", 400

    if file:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Optionally, process the image (e.g., predict nutrients)
        food_name, nutrients = predict_nutrients(filepath)

        # Return a response (e.g., render a template with the results)
        return render_template('create.html', food_name=food_name, nutrients=nutrients, uploaded_image=filename)

@app.route('/donor.html')
def donor():
    return render_template('donor.html')

@app.route('/create.html')
def create_donation():
    return render_template('create.html')

@app.route('/my_doantions.html')
def my_donations():
    return render_template('my_doantions.html')

if __name__ == '__main__':
    app.run(debug=True)
