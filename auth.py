from flask_httpauth import HTTPBasicAuth
from flask import jsonify
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user

@auth.error_handler
def unauthorized():
    return jsonify({'message': 'Unauthorized access'}), 403
