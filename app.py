from flask import Flask, render_template, request, url_for, redirect, jsonify, session
import os
from werkzeug.utils import secure_filename
from PIL import Image
from food_predictor import predict_nutrients
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text  # Import the text function

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:v@localhost:5432/FRN'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking for performance

dp = SQLAlchemy(app)

class User(dp.Model):
    __tablename__ = 'users'
    id = dp.Column(dp.Integer, primary_key=True)
    name = dp.Column(dp.String(100), nullable=False)
    email = dp.Column(dp.String(100), unique=True, nullable=False)
    password = dp.Column(dp.String(255), nullable=False)

class Donation(dp.Model):
    __tablename__ = 'donations'
    id = dp.Column(dp.Integer, primary_key=True)
    food_type = dp.Column(dp.String(100), nullable=False)
    food_preference = dp.Column(dp.String(50), nullable=False)
    quantity = dp.Column(dp.String(50), nullable=False)
    expiry = dp.Column(dp.Date, nullable=False)
    selling_price = dp.Column(dp.String(50), nullable=True, default="Free")
    location = dp.Column(dp.String(255), nullable=False)
    food_category = dp.Column(dp.String(50), nullable=False)
    storage = dp.Column(dp.String(50), nullable=False)
    contact_name = dp.Column(dp.String(100), nullable=False)
    contact_phone = dp.Column(dp.String(15), nullable=False)
    notes = dp.Column(dp.Text, nullable=True)
    image_url = dp.Column(dp.String(255), nullable=False)
    calories = dp.Column(dp.String(50), nullable=True)  # Add this
    protein = dp.Column(dp.String(50), nullable=True)   # Add this
    carbs = dp.Column(dp.String(50), nullable=True)     # Add this
    fats = dp.Column(dp.String(50), nullable=True)      # Add this

class EmergencyDonation(dp.Model):
    __tablename__ = 'emergency_donations'
    id = dp.Column(dp.Integer, primary_key=True)
    name = dp.Column(dp.String(100), nullable=False)
    phone = dp.Column(dp.String(15), nullable=False)
    email = dp.Column(dp.String(100), nullable=True)
    location = dp.Column(dp.String(255), nullable=False)
    food_type = dp.Column(dp.Text, nullable=False)
    quantity = dp.Column(dp.String(50), nullable=False)
    expiry = dp.Column(dp.DateTime, nullable=True)
    available_from = dp.Column(dp.DateTime, nullable=False)
    recurring = dp.Column(dp.String(50), nullable=True)
    donation_type = dp.Column(dp.String(50), nullable=True)
    packaged = dp.Column(dp.String(10), nullable=True)
    comments = dp.Column(dp.Text, nullable=True)

class FoodAidRequest(dp.Model):
    __tablename__ = 'food_aid_requests'
    id = dp.Column(dp.Integer, primary_key=True)
    name = dp.Column(dp.String(100), nullable=False)
    email = dp.Column(dp.String(100), nullable=False)
    phone = dp.Column(dp.String(15), nullable=False)
    location = dp.Column(dp.String(255), nullable=False)
    aid_type = dp.Column(dp.String(50), nullable=False)
    organization_type = dp.Column(dp.String(50), nullable=False)
    comments = dp.Column(dp.Text, nullable=True)

class BiofertilizerListing(dp.Model):
    __tablename__ = 'biofertilizer_listings'
    id = dp.Column(dp.Integer, primary_key=True)
    company_name = dp.Column(dp.String(100), nullable=False)
    material_type = dp.Column(dp.String(100), nullable=False)
    quantity = dp.Column(dp.Float, nullable=False)
    pickup_date = dp.Column(dp.Date, nullable=False)
    pickup_location = dp.Column(dp.String(255), nullable=False)
    contact = dp.Column(dp.String(15), nullable=False)
    timestamp = dp.Column(dp.DateTime, default=dp.func.current_timestamp(), nullable=False)

class NGORequirement(dp.Model):
    __tablename__ = 'ngo_requirements'
    id = dp.Column(dp.Integer, primary_key=True)
    ngo_name = dp.Column(dp.String(100), nullable=False)
    material_type = dp.Column(dp.String(100), nullable=False)
    quantity = dp.Column(dp.Float, nullable=False)
    pickup_date = dp.Column(dp.Date, nullable=False)
    pickup_location = dp.Column(dp.String(255), nullable=False)
    contact = dp.Column(dp.String(15), nullable=False)
    timestamp = dp.Column(dp.DateTime, default=dp.func.current_timestamp(), nullable=False)

with app.app_context():
    dp.create_all()

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

@app.route('/food_predictor.html')
def food_predictor():
    food = request.args.get('food')
    image_url = request.args.get('image_url')
    nutrients = {
        "Calories": request.args.get('calories'),
        "Protein": request.args.get('protein'),
        "Carbs": request.args.get('carbs'),
        "Fats": request.args.get('fats')
    }
    return render_template('food_predictor.html', food=food, image_url=image_url, nutrients=nutrients)

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
def render_create_donation():
    return render_template('create.html')

@app.route('/my_doantions.html')
def my_donations():
    return render_template('my_doantions.html')

@app.route('/pickup.html')
def pickup():
    return render_template('pickup.html')

@app.route('/match.html')
def match():
    return render_template('match.html')

@app.route('/ngo_listings.html')
def ngo_listings():
    return render_template('ngo_listings.html')

@app.route('/biofertilizer_listings.html')
def biofertilizer_listings():
    return render_template('biofertilizer_listings.html')

@app.route('/receiver.html')
def receiver():
    return render_template('receiver.html')

@app.route('/biofertilizer.html')
def biofertilizer():
    return render_template('biofertilizer.html')

@app.route('/apply.html')
def apply():
    return render_template('apply.html')

@app.route('/retail_surplus.html')
def retail_surplus():
    return render_template('retail_surplus.html')

@app.route('/donation_guidelines.html')
def donation_guidelines():
    return render_template('donation_guidelines.html')

@app.route('/emergency.html')
def emergency():
    return render_template('emergency.html')

@app.route('/donate_form.html')
def donate_form():
    return render_template('donate_form.html')

@app.route('/emergency_donation_dashboard.html')
def emergency_donation_dashboard():
    return render_template('emergency_donation_dashboard.html')

@app.route('/request_food_aid.html')
def request_food_aid():
    return render_template('request_food_aid.html')

@app.route('/request_dashboard.html')
def request_dashboard():
    return render_template('request_dashboard.html')

@app.route('/adopt_a_meal.html')
def adopt_a_meal():
    return render_template('adopt_a_meal.html')

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    # Check if the user already exists
    existing_user = dp.session.execute(
        text("SELECT * FROM users WHERE email = :email"), {"email": email}
    ).fetchone()

    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Insert the new user into the database
    dp.session.execute(
        text("INSERT INTO users (name, email, password) VALUES (:name, :email, :password)"),
        {"name": name, "email": email, "password": hashed_password}
    )
    dp.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Check if the user exists
    user = dp.session.execute(
        text("SELECT * FROM users WHERE email = :email"), {"email": email}
    ).fetchone()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    # Verify the password
    if not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Set session variables
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['logged_in'] = True

    print("Session data:", session)

    return jsonify({"message": "Login successful"}), 200

@app.route('/api/check-session', methods=['GET'])
def check_session():
    if 'logged_in' in session and session['logged_in']:
        return jsonify({"logged_in": True, "user_name": session.get('user_name')})
    return jsonify({"logged_in": False})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()  # Clear the session
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/create-donation', methods=['POST'])
def create_donation():
    food_image = request.files.get('food_image')
    if food_image:
        filename = secure_filename(food_image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        food_image.save(filepath)
    else:
        return jsonify({"error": "Food image is required"}), 400

    # Use the logged-in user's name from the session for contact_name
    contact_name = session.get('user_name')
    if not contact_name:
        return jsonify({"error": "Unauthorized"}), 401

    # Use food_predictor.py to predict food name and nutrients
    food_name, nutrients = predict_nutrients(filepath)

    # Save the donation data to the database
    new_donation = Donation(
        food_type=request.form.get('foodType'),
        food_preference=request.form.get('foodPreference'),
        quantity=request.form.get('quantity'),
        expiry=request.form.get('expiry'),
        selling_price=request.form.get('sellingPrice', 'Free'),
        location=request.form.get('location'),
        food_category=request.form.get('foodCategory'),
        storage=request.form.get('storage'),
        contact_name=contact_name,
        contact_phone=request.form.get('contactPhone'),
        notes=request.form.get('notes'),
        image_url=filepath,
        calories=nutrients.get('Calories'),
        protein=nutrients.get('Protein'),
        carbs=nutrients.get('Carbs'),
        fats=nutrients.get('Fats')
    )
    dp.session.add(new_donation)
    dp.session.commit()

    # Return the prediction results as JSON
    return jsonify({
        "food": food_name,
        "calories": nutrients.get("Calories"),
        "protein": nutrients.get("Protein"),
        "carbs": nutrients.get("Carbs"),
        "fats": nutrients.get("Fats"),
        "image_url": filepath
    }), 201

@app.route('/api/my-donations', methods=['GET'])
def my_donations_api():
    user_name = session.get('user_name')  # Get the logged-in user's name from the session
    if not user_name:
        return jsonify({"error": "Unauthorized"}), 401

    # Fetch donations created by the logged-in user
    donations = Donation.query.filter_by(contact_name=user_name).all()

    # Convert donations to a list of dictionaries
    donation_list = [
        {
            "food_type": donation.food_type,
            "food_preference": donation.food_preference,
            "quantity": donation.quantity,
            "expiry": donation.expiry.strftime('%Y-%m-%d'),
            "selling_price": donation.selling_price,
            "location": donation.location,
            "food_category": donation.food_category,
            "storage": donation.storage,
            "contact_name": donation.contact_name,
            "contact_phone": donation.contact_phone,
            "notes": donation.notes,
            "image_url": donation.image_url,
            "nutrients": {
                "calories": donation.calories,
                "protein": donation.protein,
                "carbs": donation.carbs,
                "fats": donation.fats
            }
        }
        for donation in donations
    ]

    return jsonify(donation_list)

@app.route('/api/emergency-donations', methods=['GET'])
def get_emergency_donations():
    donations = EmergencyDonation.query.all()

    # Convert donations to a list of dictionaries
    donation_list = [
        {
            "name": donation.name,
            "phone": donation.phone,
            "email": donation.email,
            "location": donation.location,
            "food_type": donation.food_type,
            "quantity": donation.quantity,
            "expiry": donation.expiry.strftime('%Y-%m-%d %H:%M:%S') if donation.expiry else "N/A",
            "available_from": donation.available_from.strftime('%Y-%m-%d %H:%M:%S'),
            "recurring": donation.recurring,
            "donation_type": donation.donation_type,
            "packaged": donation.packaged,
            "comments": donation.comments
        }
        for donation in donations
    ]

    return jsonify(donation_list)

@app.route('/api/emergency-donation', methods=['POST'])
def emergency_donation():
    data = request.get_json()

    # Save the donation data to the database
    new_donation = EmergencyDonation(
        name=data.get('name'),
        phone=data.get('phone'),
        email=data.get('email'),
        location=data.get('location'),
        food_type=data.get('foodType'),
        quantity=data.get('quantity'),
        expiry=data.get('expiry'),
        available_from=data.get('availableFrom'),
        recurring=data.get('recurring'),
        donation_type=data.get('donationType'),
        packaged=data.get('packaged'),
        comments=data.get('comments')
    )
    dp.session.add(new_donation)
    dp.session.commit()

    return jsonify({"message": "Donation submitted successfully!"}), 201

@app.route('/api/food-aid-request', methods=['POST'])
def food_aid_request():
    data = request.get_json()

    # Save the request data to the database
    new_request = FoodAidRequest(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        location=data.get('location'),
        aid_type=data.get('aidType'),
        organization_type=data.get('organizationType'),
        comments=data.get('comments')
    )
    dp.session.add(new_request)
    dp.session.commit()

    return jsonify({"message": "Food aid request submitted successfully!"}), 201

@app.route('/api/food-aid-requests', methods=['GET'])
def get_food_aid_requests():
    requests = FoodAidRequest.query.all()

    # Convert requests to a list of dictionaries
    request_list = [
        {
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "location": request.location,
            "aidType": request.aid_type,
            "organizationType": request.organization_type,
            "comments": request.comments
        }
        for request in requests
    ]

    return jsonify(request_list)

@app.route('/api/add-biofertilizer', methods=['POST'])
def add_biofertilizer():
    data = request.json
    new_listing = BiofertilizerListing(
        company_name=data['companyName'],
        material_type=data['materialType'],
        quantity=data['quantity'],
        pickup_date=data['pickupDate'],
        pickup_location=data['pickupLocation'],
        contact=data['contact']
    )
    dp.session.add(new_listing)
    dp.session.commit()
    return jsonify({"message": "Biofertilizer listing added successfully!"}), 201

@app.route('/api/get-biofertilizers', methods=['GET'])
def get_biofertilizers():
    listings = BiofertilizerListing.query.all()
    result = [
        {
            "id": listing.id,
            "companyName": listing.company_name,
            "materialType": listing.material_type,
            "quantity": listing.quantity,
            "pickupDate": listing.pickup_date.strftime('%Y-%m-%d'),
            "pickupLocation": listing.pickup_location,
            "contact": listing.contact,
            "timestamp": listing.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for listing in listings
    ]
    return jsonify(result)

@app.route('/api/add-ngo-requirement', methods=['POST'])
def add_ngo_requirement():
    data = request.json
    new_requirement = NGORequirement(
        ngo_name=data['ngoName'],
        material_type=data['materialType'],
        quantity=data['quantity'],
        pickup_date=data['pickupDate'],
        pickup_location=data['pickupLocation'],
        contact=data['contact']
    )
    dp.session.add(new_requirement)
    dp.session.commit()
    return jsonify({"message": "NGO requirement added successfully!"}), 201

@app.route('/api/get-ngo-requirements', methods=['GET'])
def get_ngo_requirements():
    requirements = NGORequirement.query.all()
    result = [
        {
            "id": req.id,
            "ngoName": req.ngo_name,
            "materialType": req.material_type,
            "quantity": req.quantity,
            "pickupDate": req.pickup_date.strftime('%Y-%m-%d'),
            "pickupLocation": req.pickup_location,
            "contact": req.contact,
            "timestamp": req.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for req in requirements
    ]
    return jsonify(result)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Use the PORT environment variable or default to 5000
    app.run(host="0.0.0.0", port=port)  # Bind to 0.0.0.0 to make it accessible externally
