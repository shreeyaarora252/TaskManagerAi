from flask import request, jsonify, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app import db

auth_bp = Blueprint("auth", __name__)

#signup
@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        # Check if all required fields are provided
        if not username or not email or not password:
            return jsonify({'message': 'Username, email, and password are required'}), 400

        # Check if username or email already exists
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({'message': 'Username or email already exists'}), 400

        # Hash the password before saving
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#login
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()  # Trim spaces
        password = data.get('password', '').strip()

        # Validate input
        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400

        # Fetch user from database
        user = User.query.filter_by(username=username).first()

        # Validate user and password
        if not user or not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid credentials'}), 401

        # Generate JWT token
        access_token = create_access_token(identity=str(user.id))

        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500     