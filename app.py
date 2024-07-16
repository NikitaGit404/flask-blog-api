from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from models import User, BlogPost, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user

@auth.error_handler
def unauthorized():
    return jsonify({'message': 'Unauthorized access'}), 403

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful'}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/posts', methods=['POST'])
@auth.login_required
def create_post():
    data = request.get_json()
    new_post = BlogPost(title=data['title'], content=data['content'], user_id=auth.current_user().id)
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.to_dict()), 201

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = BlogPost.query.all()
    return jsonify([post.to_dict() for post in posts]), 200

@app.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = BlogPost.query.get_or_404(id)
    return jsonify(post.to_dict()), 200

@app.route('/posts/<int:id>', methods=['PUT'])
@auth.login_required
def update_post(id):
    post = BlogPost.query.get_or_404(id)
    data = request.get_json()
    if post.user_id != auth.current_user().id:
        return jsonify({'message': 'Unauthorized'}), 403
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    db.session.commit()
    return jsonify(post.to_dict()), 200

@app.route('/posts/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_post(id):
    post = BlogPost.query.get_or_404(id)
    if post.user_id != auth.current_user().id:
        return jsonify({'message': 'Unauthorized'}), 403
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
