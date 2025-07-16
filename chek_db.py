
import os
from sqlalchemy import create_engine, inspect
from app.config import Config


db_uri = Config.SQLALCHEMY_DATABASE_URI
print(f"Mencoba terhubung ke: {db_uri}\n")

try:
    engine = create_engine(db_uri)
    with engine.connect() as connection:
        inspector = inspect(engine)
        schemas = inspector.get_schema_names()

        print("Koneksi BERHASIL!")
        print("Skema yang ditemukan:", schemas)

        if 'public' in schemas:
            tables = inspector.get_table_names(schema='public')
            if not tables:
                print("\n✅ STATUS: Database BERSIH. Tidak ada tabel ditemukan di skema 'public'.")
            else:
                print("\n❌ STATUS: DATABASE TIDAK KOSONG! Tabel yang ditemukan:")
                for table in tables:
                    print(f"  - {table}")
        else:
            print("\nWARNING: Skema 'public' tidak ditemukan.")

except Exception as e:
    print(f"\n❌ KONEKSI GAGAL. Error: {e}")