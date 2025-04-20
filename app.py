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

@app.route('/food-predictor', methods=['POST'])
def food_predictor():
    if 'food_image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['food_image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Call the food predictor function
        food_name, nutrients = predict_nutrients(filepath)

        # Render the food_predictor.html page with the prediction results
        rendered_html = render_template(
            'food_predictor.html',
            food=food_name,
            nutrients=nutrients,
            image_url=url_for('static', filename=f'uploads/{filename}')
        )

        # Return the nutrient data, image URL, and rendered HTML as JSON
        return jsonify({
            "image_url": url_for('static', filename=f'uploads/{filename}'),
            "nutrients": nutrients,
            "html": rendered_html
        })

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

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Use the PORT environment variable or default to 5000
    app.run(host="0.0.0.0", port=port)  # Bind to 0.0.0.0 to make it accessible externally
