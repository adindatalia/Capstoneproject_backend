from flask import Blueprint, request, jsonify
from .models import db, Pengguna, Resep, Favorit
from . import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import traceback

auth = Blueprint('auth', __name__)


@auth.errorhandler(422)
def handle_unprocessable_entity(e):
    print(f"JWT Error 422: {e}")
    print(f"Request headers: {dict(request.headers)}")
    return jsonify({"error": "Token tidak valid atau sudah kedaluwarsa. Silakan login ulang."}), 422

@auth.errorhandler(401)
def handle_unauthorized(e):
    print(f"JWT Error 401: {e}")
    return jsonify({"error": "Token tidak ditemukan. Silakan login terlebih dahulu."}), 401

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nama = data.get('nama')
    email = data.get('email')
    password = data.get('password')
    if not nama or not email or not password: return jsonify({"error": "Data tidak lengkap"}), 400
    if Pengguna.query.filter_by(email=email).first(): return jsonify({"error": "Email sudah terdaftar"}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    pengguna_baru = Pengguna(nama=nama, email=email, password=hashed_password)
    db.session.add(pengguna_baru)
    db.session.commit()
    return jsonify({"message": "Registrasi berhasil!"}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    pengguna = Pengguna.query.filter_by(email=email).first()
    if not pengguna or not bcrypt.check_password_hash(pengguna.password, password):
        return jsonify({"error": "Email atau password salah"}), 401
 
    access_token = create_access_token(identity=str(pengguna.id))
    return jsonify(
        access_token=access_token, 
        user_data={
            "id": pengguna.id,
            "nama": pengguna.nama,
            "email": pengguna.email
        }
    ), 200
@auth.route('/profile')
@jwt_required() 
def profile():
    current_user_id = int(get_jwt_identity())  
    user = Pengguna.query.get(current_user_id)
    if not user: return jsonify({"error": "Pengguna tidak ditemukan"}), 404
    return jsonify({"id": user.id, "nama": user.nama, "email": user.email}), 200

@auth.route('/favorite/<int:recipe_id>', methods=['POST'])
@jwt_required()
def toggle_favorite(recipe_id):
    """
    Menambah atau menghapus resep dari favorit.
    Jika sudah ada, hapus. Jika belum, tambah. (Toggle)
    """
    try:
        current_user_id = int(get_jwt_identity())  
        print(f"Toggle favorite - User ID: {current_user_id}, Recipe ID: {recipe_id}")
        
        resep = Resep.query.get(recipe_id)
        if not resep:
            return jsonify({"error": "Resep tidak ditemukan"}), 404

        favorite_item = Favorit.query.filter_by(pengguna_id=current_user_id, resep_id=recipe_id).first()

        if favorite_item:
            
            db.session.delete(favorite_item)
            db.session.commit()
            print(f"Favorit dihapus untuk user {current_user_id}, recipe {recipe_id}")
            return jsonify({"message": "Resep berhasil dihapus dari favorit", "isFavorited": False}), 200
        else:
            
            new_favorite = Favorit(pengguna_id=current_user_id, resep_id=recipe_id)
            db.session.add(new_favorite)
            db.session.commit()
            print(f"Favorit ditambah untuk user {current_user_id}, recipe {recipe_id}")
            return jsonify({"message": "Resep berhasil ditambahkan ke favorit", "isFavorited": True}), 201
    except Exception as e:
        print(f"Error dalam toggle_favorite: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500

@auth.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    """Mengambil semua resep favorit dari pengguna yang sedang login."""
    try:
        current_user_id = int(get_jwt_identity()) 
        print(f"Get favorites - User ID: {current_user_id}")
        
        
        favorite_recipes = db.session.query(Resep).join(Favorit).filter(Favorit.pengguna_id == current_user_id).order_by(Favorit.id.desc()).all()
        results = [
            {"id": resep.id, "title": resep.title, "image": resep.image, "deskripsi_singkat": resep.deskripsi_singkat} 
            for resep in favorite_recipes
        ]
        print(f"Found {len(results)} favorites for user {current_user_id}")
        return jsonify(results), 200
    except Exception as e:
        print(f"Error dalam get_favorites: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500

@auth.route('/favorites/status/<int:recipe_id>', methods=['GET'])
@jwt_required()
def get_favorite_status(recipe_id):
    """Mengecek apakah satu resep sudah difavoritkan oleh pengguna."""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string to int
        print(f"Get favorite status - User ID: {current_user_id}, Recipe ID: {recipe_id}")
        
        is_favorited = Favorit.query.filter_by(pengguna_id=current_user_id, resep_id=recipe_id).first()
        result = is_favorited is not None
        print(f"Favorite status for user {current_user_id}, recipe {recipe_id}: {result}")
        return jsonify(isFavorited=result), 200
    except Exception as e:
        print(f"Error dalam get_favorite_status: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500

@auth.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint without JWT requirement"""
    return jsonify({"message": "Test endpoint working"}), 200

@auth.route('/test-jwt', methods=['GET'])
@jwt_required()
def test_jwt_endpoint():
    """Test endpoint with JWT requirement"""
    try:
        current_user_id = int(get_jwt_identity())  
        return jsonify({"message": "JWT working", "user_id": current_user_id}), 200
    except Exception as e:
        print(f"JWT Test Error: {e}")
        return jsonify({"error": str(e)}), 500

