
import pandas as pd
import re
import os
from app import create_app
from app.models import db, Resep, Bahan, ResepBahan, LangkahMemasak

FILE_PATH = 'dataset_resep.csv'

def parse_steps(steps_text):
    if not isinstance(steps_text, str):
        return []
    steps = re.split(r'\d+\)', steps_text)
    return [step.strip() for step in steps if step and step.strip()]

def clean_ingredient_name(name):
    """Fungsi pembersihan yang lebih agresif untuk nama bahan."""
    name = name.strip().lower()

    name = re.sub(r'^[^a-zA-Z]+', '', name)
    return name

def seed_database():
    app = create_app()
    with app.app_context():
        if Resep.query.count() > 0:
            print("Database sudah berisi data. Proses seeding dilewati. Untuk menjalankan ulang, reset database terlebih dahulu.")
            return

        print(f"Membaca file CSV dari: {FILE_PATH}")
        try:
            df = pd.read_csv(FILE_PATH)
        except FileNotFoundError:
            print(f"ERROR: File tidak ditemukan di '{FILE_PATH}'.")
            return

        print(f"Ditemukan {len(df)} resep. Memulai proses seeding...")
        bahan_cache = {} 

        for index, row in df.iterrows():
            try:
                if 'Title' not in row or pd.isna(row['Title']):
                    continue
                
                resep_obj = Resep(
                    title=row['Title'],
                    deskripsi_singkat=f"Resep lezat untuk {row['Title']}",
                    image=row['URL'] if 'URL' in row else None
                )
                db.session.add(resep_obj)
                db.session.flush()

                if 'Ingredients Cleaned' in row and pd.notna(row['Ingredients Cleaned']):
                    ingredients_list = str(row['Ingredients Cleaned']).split(',')
                    for ing_name in ingredients_list:
                        
                   
                        clean_ing_name = clean_ingredient_name(ing_name)
                        
                       
                        if len(clean_ing_name) < 2 or len(clean_ing_name) > 50 or len(clean_ing_name.split()) > 4:
                            continue
                       
                        
                        bahan_obj = bahan_cache.get(clean_ing_name)
                        if not bahan_obj:
                            bahan_obj = Bahan.query.filter_by(nama_bahan=clean_ing_name).first()
                            if not bahan_obj:
                                bahan_obj = Bahan(
                                    nama_bahan=clean_ing_name,
                                    kategori=row.get('Category', 'Lainnya').lower()
                                )
                                db.session.add(bahan_obj)
                                db.session.flush()
                            bahan_cache[clean_ing_name] = bahan_obj
                        
                        resep_bahan_obj = ResepBahan(resep_id=resep_obj.id, bahan_id=bahan_obj.id)
                        db.session.add(resep_bahan_obj)

                if 'Steps' in row and pd.notna(row['Steps']):
                    langkah_list = parse_steps(str(row['Steps']))
                    for i, langkah_desc in enumerate(langkah_list):
                        langkah_obj = LangkahMemasak(
                            resep_id=resep_obj.id,
                            nomor_langkah=i + 1,
                            deskripsi=langkah_desc
                        )
                        db.session.add(langkah_obj)
                
                if (index + 1) % 500 == 0:
                    print(f"Memproses resep {index + 1}/{len(df)}...")
                    db.session.commit() 

            except Exception as e:
                print(f"ERROR di baris {index + 1} ({row.get('Title', 'Tanpa Judul')}): {e}")
                db.session.rollback()
                continue
        
        try:
            print("Menyimpan sisa data ke database...")
            db.session.commit()
            print("\nSUCCESS: Database berhasil di-seed dengan data yang lebih bersih!")
        except Exception as e:
            print(f"\nERROR saat commit final: {e}")
            db.session.rollback()

if __name__ == '__main__':
    seed_database()