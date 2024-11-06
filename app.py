import os
import re
from flask import Flask, render_template, redirect, url_for, request, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

client = MongoClient('mongodb://localhost:27017/')

db = client['Database_Nou']
users_collection = db['users']
Admins_collection = db['Admin']


# Kodingan Home
@app.route('/')
def home():
    return render_template('home.html')


# Kodingan User
@app.route('/register', methods=['GET', 'POST'])
def userRegister():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Validasi input kosong
        if not username or not email or not password:
            flash('Semua kolom harus diisi!', 'error')
            return redirect('/register')
        
        # Cek apakah username telah digunakan
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            flash('Username sudah digunakan!', 'error')
            return redirect('/register')
        
        # Cek format email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('email tidak valid', 'error')
            return redirect(url_for('register'))
        
        # Cek apakah email telah digunakan
        existing_email = users_collection.find_one({'email': email})
        if existing_email:
            flash('Email sudah digunakan!', 'error')
            return redirect('/register')
        
        # Cek panjang password
        if len(password) < 8:
            flash('Password harus minimal 8 karakter!', 'error')
            return redirect('/register')
        
        # Jika semua validasi berhasil, buat user baru
        hashed_password = generate_password_hash(password)
        
        # Simpan ke database
        new_user = {
            'username': username,
            'email': email,
            'password': hashed_password
        }
        
        try:
            users_collection.insert_one(new_user)
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect('/login')
        except Exception as e:
            flash('Terjadi kesalahan. Silakan coba lagi.', 'error')
            return redirect('/register')
            
    # Jika method GET, tampilkan form register
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def userLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_collection.find_one({'username': username})
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login berhasil!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Username atau password salah!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def userLogout():
    session.pop('username', None)
    flash('Anda telah logout.', 'success')
    return redirect(url_for('home'))


# Kodingan Admin
@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True) 