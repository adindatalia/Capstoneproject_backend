
from flask import Blueprint, request, jsonify
import joblib, os, numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import db, Resep, Bahan, ResepBahan, LangkahMemasak
from collections import defaultdict

main = Blueprint('main', __name__)
ml_models = {}

def load_models():
    """Memuat semua model .pkl dari folder 'models'."""
    print("Memuat model Machine Learning...")
    try:

        base_path = os.path.join(os.path.dirname(__file__), '..', 'models')

        print(f"Mencari model di path: {base_path}")
        
        ml_models['vectorizer'] = joblib.load(os.path.join(base_path, 'tfidf_vectorizer_final.pkl'))
        ml_models['tfidf_matrix'] = joblib.load(os.path.join(base_path, 'tfidf_matrix_final.pkl'))
        ml_models['recipe_id_map'] = joblib.load(os.path.join(base_path, 'recipe_id_map_final.pkl'))
        
        print("✅ Model berhasil dimuat.")
    except FileNotFoundError as e:
        print(f"===================================================================")
        print(f"⚠️ Peringatan PENTING: File model .pkl tidak ditemukan!")
        print(f"   Error: {e}")
        print(f"   PASTIKAN 3 file .pkl Anda ada di dalam folder 'backend/models/'")
        print(f"===================================================================")

load_models()

def get_recommendations_from_model(ingredients_text, top_n=20):
    if 'vectorizer' not in ml_models: return []
    input_vector = ml_models['vectorizer'].transform([ingredients_text])
    cosine_sim = cosine_similarity(input_vector, ml_models['tfidf_matrix']).flatten()
    top_indices = np.argsort(cosine_sim)[::-1]
    
    recommended_ids = []
    for idx in top_indices:
        if cosine_sim[idx] > 0.01:
            recommended_ids.append(int(ml_models['recipe_id_map'][idx]))
        if len(recommended_ids) == top_n: break
            
    return recommended_ids

def normalize_ingredient_name(ingredient_name):
    """
    Normalize ingredient names to standard forms for better matching
    """
    ingredient = ingredient_name.lower().strip()
    

    if 'bawang merah' in ingredient:
        return 'bawang merah'
    elif 'bawang putih' in ingredient:
        return 'bawang putih'
    elif 'bawang bombai' in ingredient or 'bawang bombay' in ingredient:
        return 'bawang bombai'
    elif 'daun bawang' in ingredient:
        return 'daun bawang'
    elif 'bawang prei' in ingredient or 'bawang pre' in ingredient:
        return 'bawang prei'
    

    elif 'daging sapi' in ingredient or 'sapi' in ingredient:
        return 'daging sapi'
    elif 'daging ayam' in ingredient or 'ayam' in ingredient:
        return 'ayam'
    elif 'ikan' in ingredient:
        return 'ikan'
    elif 'udang' in ingredient:
        return 'udang'
    elif 'telur' in ingredient:
        return 'telur'
    elif 'tahu' in ingredient:
        return 'tahu'
    elif 'tempe' in ingredient:
        return 'tempe'
    

    elif 'wortel' in ingredient:
        return 'wortel'
    elif 'kentang' in ingredient:
        return 'kentang'
    elif 'tomat' in ingredient:
        return 'tomat'
    elif 'cabai' in ingredient or 'cabe' in ingredient:
        return 'cabai'
    elif 'seledri' in ingredient:
        return 'seledri'

    elif 'garam' in ingredient:
        return 'garam'
    elif 'merica' in ingredient or 'lada' in ingredient:
        return 'lada'
    elif 'kunyit' in ingredient:
        return 'kunyit'
    elif 'ketumbar' in ingredient:
        return 'ketumbar'
    elif 'jahe' in ingredient:
        return 'jahe'
    elif 'lengkuas' in ingredient:
        return 'lengkuas'
    

    elif 'beras' in ingredient or 'nasi' in ingredient:
        return 'beras'
    elif 'mie' in ingredient or 'mee' in ingredient:
        return 'mie'
    elif 'tepung' in ingredient:
        return 'tepung'
    

    return ingredient

@main.route('/ingredients-by-category', methods=['GET'])
def get_all_ingredients():
    try:

        semua_bahan = Bahan.query.all()
        
        
        normalized_ingredients = set()
        ingredient_count = {}  
        proper_categories = {
            'Protein': [],
            'Sayuran': [],
            'Bumbu': [],
            'Biji-bijian': [],
            'Lainnya': []
        }
        
       
        for bahan in semua_bahan:
            normalized_name = normalize_ingredient_name(bahan.nama_bahan)
            if normalized_name not in ingredient_count:
                ingredient_count[normalized_name] = 0
            ingredient_count[normalized_name] += 1
        
      
        min_usage = 10
        popular_ingredients = {name: count for name, count in ingredient_count.items() 
                             if count >= min_usage}
        
       
        for ingredient_name, usage_count in popular_ingredients.items():
           
            if any(protein in ingredient_name for protein in ['ayam', 'daging sapi', 'ikan', 'udang', 'telur', 'tahu', 'tempe']):
                proper_categories['Protein'].append(ingredient_name.title())
            elif any(veg in ingredient_name for veg in ['bawang', 'wortel', 'kentang', 'tomat', 'seledri', 'sawi', 'kangkung', 'bayam']):
                proper_categories['Sayuran'].append(ingredient_name.title())
            elif any(spice in ingredient_name for spice in ['garam', 'lada', 'merica', 'kunyit', 'ketumbar', 'jahe', 'lengkuas', 'cabai', 'cabe']):
                proper_categories['Bumbu'].append(ingredient_name.title())
            elif any(grain in ingredient_name for grain in ['beras', 'nasi', 'mie', 'tepung']):
                proper_categories['Biji-bijian'].append(ingredient_name.title())
            else:
                proper_categories['Lainnya'].append(ingredient_name.title())
        

        max_per_category = 20
        for category in proper_categories:
            proper_categories[category] = sorted(proper_categories[category])[:max_per_category]
        
        print(f"Returning ingredients: {sum(len(v) for v in proper_categories.values())} total")
        return jsonify(proper_categories), 200
    except Exception as e:
        print(f"Error in get_all_ingredients: {e}")
        return jsonify({"error": str(e)}), 500

@main.route('/recommendations', methods=['POST'])
def recommend():
    data = request.get_json()
    ingredients_list = data.get('ingredients', [])
    if not ingredients_list: return jsonify({"error": "Input 'ingredients' is required!"}), 400
    
   
    normalized_ingredients = [normalize_ingredient_name(ingredient) for ingredient in ingredients_list]
    input_text = ' '.join(normalized_ingredients).lower()
    
    print(f"Original ingredients: {ingredients_list}")
    print(f"Normalized ingredients: {normalized_ingredients}")
    print(f"Search text: {input_text}")
    
    recommended_ids = get_recommendations_from_model(input_text)
    if not recommended_ids: return jsonify([]), 200
    resep_rekomendasi = Resep.query.filter(Resep.id.in_(recommended_ids)).all()
    resep_map = {resep.id: resep for resep in resep_rekomendasi}
    sorted_resep = [resep_map[id] for id in recommended_ids if id in resep_map]
    results = [{"id": resep.id, "title": resep.title, "image": resep.image, "deskripsi_singkat": resep.deskripsi_singkat} for resep in sorted_resep]
    return jsonify(results), 200

@main.route('/recipe/<int:recipe_id>', methods=['GET'])
def get_recipe_details(recipe_id):
    try:
        resep = Resep.query.get(recipe_id)
        if not resep: return jsonify({"error": "Resep tidak ditemukan"}), 404

        resep_bahan_list = db.session.query(ResepBahan, Bahan).join(Bahan).filter(ResepBahan.resep_id == recipe_id).all()
        bahan_list = [f"{rb.jumlah or ''} {rb.satuan or ''} {bahan.nama_bahan}".strip() for rb, bahan in resep_bahan_list]
        
        langkah_list = [langkah.deskripsi for langkah in sorted(resep.langkah, key=lambda x: x.nomor_langkah)]
        result = {"id": resep.id, "title": resep.title, "image": resep.image, "description": resep.deskripsi_singkat, "ingredients": bahan_list, "steps": langkah_list}
        return jsonify(result), 200
    except Exception as e:
        print(f"Error di get_recipe_details: {e}") 
        return jsonify({"error": str(e)}), 500

@main.route('/recipes/latest', methods=['GET'])
def get_latest_recipes():
    try:
        resep_terbaru = Resep.query.order_by(db.func.random()).limit(50).all()
        results = [{"id": resep.id, "title": resep.title, "image": resep.image, "deskripsi_singkat": resep.deskripsi_singkat} for resep in resep_terbaru]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

