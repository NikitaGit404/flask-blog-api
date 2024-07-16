import base64
import unittest
import json
from app import app, db
from models import User, BlogPost

class BlogTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_blog.db'

        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_signup(self):
        response = self.client.post('/signup', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('User created successfully', response.get_data(as_text=True))

    def test_signup_existing_user(self):
        self.client.post('/signup', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')

        response = self.client.post('/signup', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('User already exists', response.get_data(as_text=True))

    def test_signin(self):
        self.client.post('/signup', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')

        response = self.client.post('/signin', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Login successful', response.get_data(as_text=True))

    def test_signin_invalid_credentials(self):
        self.client.post('/signup', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')

        response = self.client.post('/signin', data=json.dumps({
            'username': 'testuser',
            'password': 'wrongpassword'
        }), content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid credentials', response.get_data(as_text=True))

    def test_create_post(self):
        self.client.post('/signup', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')

        response = self.client.post('/signin', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/posts', data=json.dumps({
            'title': 'My First Blog Post',
            'content': 'This is the content of my first blog post.'
        }), content_type='application/json', headers={
            'Authorization': 'Basic ' + base64.b64encode(b'testuser:testpassword').decode('utf-8')
        })
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('My First Blog Post', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
