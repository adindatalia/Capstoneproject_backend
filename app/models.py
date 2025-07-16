
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Pengguna(db.Model):
    __tablename__ = 'pengguna'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    favorit = db.relationship('Favorit', backref='pengguna', lazy=True, cascade="all, delete-orphan")
    riwayat_pencarian = db.relationship('RiwayatPencarian', backref='pengguna', lazy=True, cascade="all, delete-orphan")


class Bahan(db.Model):
    __tablename__ = 'bahan'
    id = db.Column(db.Integer, primary_key=True)
    nama_bahan = db.Column(db.String(250), nullable=False, unique=True) 
    kategori = db.Column(db.String(50), nullable=False, index=True) 


class Resep(db.Model):
    __tablename__ = 'resep'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    deskripsi_singkat = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    favorit = db.relationship('Favorit', backref='resep', lazy=True, cascade="all, delete-orphan")
    langkah = db.relationship('LangkahMemasak', backref='resep', lazy=True, cascade="all, delete-orphan") 
    bahan = db.relationship('Bahan', secondary='resep_bahan', lazy='subquery',
                            backref=db.backref('resep', lazy=True)) 

class ResepBahan(db.Model):
    __tablename__ = 'resep_bahan'
    id = db.Column(db.Integer, primary_key=True)
    resep_id = db.Column(db.Integer, db.ForeignKey('resep.id'), nullable=False)
    bahan_id = db.Column(db.Integer, db.ForeignKey('bahan.id'), nullable=False) 
    jumlah = db.Column(db.String(50)) 
    satuan = db.Column(db.String(50)) 

class LangkahMemasak(db.Model):
    __tablename__ = 'langkah_memasak'
    id = db.Column(db.Integer, primary_key=True)
    resep_id = db.Column(db.Integer, db.ForeignKey('resep.id'), nullable=False)
    nomor_langkah = db.Column(db.Integer, nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)

class Favorit(db.Model):
    __tablename__ = 'favorit'
    id = db.Column(db.Integer, primary_key=True)
    pengguna_id = db.Column(db.Integer, db.ForeignKey('pengguna.id'), nullable=False)
    resep_id = db.Column(db.Integer, db.ForeignKey('resep.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('pengguna_id', 'resep_id', name='unique_pengguna_resep'),)

