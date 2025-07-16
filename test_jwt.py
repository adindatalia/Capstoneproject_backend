
from app import create_app
from flask_jwt_extended import create_access_token, decode_token
from app.models import db, Pengguna

app = create_app()

with app.app_context():
    
    print("Testing JWT functionality...")

    test_user_id = "1"  
    token = create_access_token(identity=test_user_id)
    print(f"Created token: {token[:50]}...")
    
    try:
  
        decoded = decode_token(token)
        print(f"Decoded token successfully: {decoded}")
        print(f"User ID from token: {decoded['sub']}")
    except Exception as e:
        print(f"Error decoding token: {e}")

    print(f"JWT Secret Key: {app.config.get('JWT_SECRET_KEY')}")
    print(f"Secret Key: {app.config.get('SECRET_KEY')}")
