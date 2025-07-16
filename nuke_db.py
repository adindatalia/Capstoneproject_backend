
import os
from sqlalchemy import create_engine, text
from app.config import Config
import sys


confirm = input("Anda yakin ingin MENGHAPUS SEMUA TABEL di database? Ketik 'ya' untuk melanjutkan: ")
if confirm.lower() != 'ya':
    print("Operasi dibatalkan.")
    sys.exit()


db_uri = Config.SQLALCHEMY_DATABASE_URI
print(f"\nMenghubungkan ke: {db_uri}")

try:
    engine = create_engine(db_uri)
    with engine.connect() as connection:
        print("Koneksi berhasil. Mencoba menjalankan DROP dan CREATE SCHEMA...")

        connection.execution_options(isolation_level="AUTOCOMMIT")

        connection.execute(text("DROP SCHEMA public CASCADE;"))
        connection.execute(text("CREATE SCHEMA public;"))

        print("\n✅ Perintah DROP dan CREATE SCHEMA berhasil dieksekusi via kode.")
        print("Database Anda sekarang dijamin kosong.")

except Exception as e:
    print(f"\n❌ Terjadi error saat mencoba mereset DB: {e}")