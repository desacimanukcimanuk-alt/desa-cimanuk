# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import mysql.connector
from config import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    DB_PORT,
    SECRET_KEY,
    UPLOAD_FOLDER
)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder upload ada
for subfolder in ['galeri', 'dokumentasi', 'pengaduan']:
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], subfolder), exist_ok=True)

def get_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )

# ============================================
# FRONTEND
# ============================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/frontend')
def frontend_data():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Data tentang
    cursor.execute("SELECT * FROM tentang WHERE id=1")
    tentang = cursor.fetchone()
    # 6 galeri terbaru
    cursor.execute("SELECT * FROM galeri ORDER BY created_at DESC LIMIT 6")
    recent_galeri = cursor.fetchall()
    # 5 dokumentasi terbaru
    cursor.execute("SELECT * FROM dokumentasi ORDER BY created_at DESC LIMIT 5")
    recent_dok = cursor.fetchall()
    # Semua galeri (untuk section galeri)
    cursor.execute("SELECT * FROM galeri ORDER BY created_at DESC")
    all_galeri = cursor.fetchall()
    # Semua dokumentasi
    cursor.execute("SELECT * FROM dokumentasi ORDER BY created_at DESC")
    all_dok = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({
        'tentang': tentang,
        'recent_galeri': recent_galeri,
        'recent_dokumentasi': recent_dok,
        'all_galeri': all_galeri,
        'all_dokumentasi': all_dok
    })

@app.route('/api/pengaduan', methods=['POST'])
def submit_pengaduan():
    judul = request.form['judul']
    isi = request.form['isi']

    foto = request.files.get('foto')
    foto_filename = None

    if foto and foto.filename != '':
        filename = secure_filename(foto.filename)
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], 'pengaduan', filename))
        foto_filename = filename

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pengaduan
        (judul, isi, foto, status)
        VALUES (%s,%s,%s,'Menunggu')
    """, (
        judul,
        isi,
        foto_filename
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "status":"success",
        "message":"Pengaduan berhasil dikirim."
    })

# ============================================
# ADMIN AUTH
# ============================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        # Prepared statement sederhana
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        if admin:
            session['admin'] = admin
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Username atau password salah.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# Decorator untuk proteksi dashboard
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ============================================
# API ADMIN
# ============================================
@app.route('/admin/dashboard-stats')
@login_required
def dashboard_stats():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM galeri")
    total_galeri = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM dokumentasi")
    total_dok = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM pengaduan")
    total_pengaduan = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM pengaduan WHERE status='Menunggu'")
    menunggu = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM pengaduan WHERE status='Diproses'")
    diproses = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM pengaduan WHERE status='Selesai'")
    selesai = cursor.fetchone()['total']
    cursor.close()
    conn.close()
    return jsonify({
        'total_galeri': total_galeri,
        'total_dokumentasi': total_dok,
        'total_pengaduan': total_pengaduan,
        'menunggu': menunggu,
        'diproses': diproses,
        'selesai': selesai
    })

# --- TENTANG ---
@app.route('/admin/tentang', methods=['GET'])
@login_required
def get_tentang():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tentang WHERE id=1")
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/admin/tentang/update', methods=['POST'])
@login_required
def update_tentang():
    # Ambil data dari form
    profil = request.form['profil']
    sejarah = request.form['sejarah']
    visi = request.form['visi']
    misi = request.form['misi']
    struktur = request.form['struktur_organisasi']
    sambutan = request.form['sambutan_lurah']
    alamat = request.form['alamat']
    telepon = request.form['telepon']
    email = request.form['email']
    maps = request.form['maps_embed']
    jml_penduduk = request.form.get('jumlah_penduduk', None)
    jml_kk = request.form.get('jumlah_kk', None)
    luas = request.form.get('luas_wilayah', '')
    logo_file = request.files.get('logo')
    logo_filename = None
    if logo_file and logo_file.filename != '':
        filename = secure_filename(logo_file.filename)
        logo_file.save(os.path.join('static/assets/logo', filename))
        logo_filename = filename
    conn = get_db()
    cursor = conn.cursor()
    if logo_filename:
        cursor.execute("""
            UPDATE tentang SET logo=%s, profil=%s, sejarah=%s, visi=%s, misi=%s,
            struktur_organisasi=%s, sambutan_lurah=%s, alamat=%s, telepon=%s,
            email=%s, maps_embed=%s, jumlah_penduduk=%s, jumlah_kk=%s, luas_wilayah=%s
            WHERE id=1
        """, (logo_filename, profil, sejarah, visi, misi, struktur, sambutan,
              alamat, telepon, email, maps, jml_penduduk, jml_kk, luas))
    else:
        cursor.execute("""
            UPDATE tentang SET profil=%s, sejarah=%s, visi=%s, misi=%s,
            struktur_organisasi=%s, sambutan_lurah=%s, alamat=%s, telepon=%s,
            email=%s, maps_embed=%s, jumlah_penduduk=%s, jumlah_kk=%s, luas_wilayah=%s
            WHERE id=1
        """, (profil, sejarah, visi, misi, struktur, sambutan,
              alamat, telepon, email, maps, jml_penduduk, jml_kk, luas))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

# --- GALERI ---
@app.route('/admin/galeri', methods=['GET'])
@login_required
def admin_galeri_list():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM galeri ORDER BY created_at DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/admin/galeri/add', methods=['POST'])
@login_required
def admin_galeri_add():
    judul = request.form['judul']
    kategori = request.form['kategori']
    file = request.files['foto']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'galeri', filename))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO galeri (judul, kategori, foto) VALUES (%s, %s, %s)", (judul, kategori, filename))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/admin/galeri/update', methods=['POST'])
@login_required
def admin_galeri_update():
    id_ = request.form['id']
    judul = request.form['judul']
    kategori = request.form['kategori']
    file = request.files.get('foto')
    if file and file.filename != '':
        # Hapus foto lama
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT foto FROM galeri WHERE id=%s", (id_,))
        old = cursor.fetchone()
        if old and old['foto']:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'galeri', old['foto'])
            if os.path.exists(old_path):
                os.remove(old_path)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'galeri', filename))
        cursor.execute("UPDATE galeri SET judul=%s, kategori=%s, foto=%s WHERE id=%s", (judul, kategori, filename, id_))
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE galeri SET judul=%s, kategori=%s WHERE id=%s", (judul, kategori, id_))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/admin/galeri/delete', methods=['POST'])
@login_required
def admin_galeri_delete():
    id_ = request.form['id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT foto FROM galeri WHERE id=%s", (id_,))
    old = cursor.fetchone()
    if old and old['foto']:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'galeri', old['foto'])
        if os.path.exists(old_path):
            os.remove(old_path)
    cursor.execute("DELETE FROM galeri WHERE id=%s", (id_,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

# --- DOKUMENTASI ---
@app.route('/admin/dokumentasi', methods=['GET'])
@login_required
def admin_dok_list():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dokumentasi ORDER BY created_at DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/admin/dokumentasi/add', methods=['POST'])
@login_required
def admin_dok_add():
    nama = request.form['nama_dokumen']
    kategori = request.form['kategori']
    file = request.files['file_dok']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'dokumentasi', filename))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dokumentasi (nama_dokumen, kategori, file_path) VALUES (%s, %s, %s)", (nama, kategori, filename))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/admin/dokumentasi/update', methods=['POST'])
@login_required
def admin_dok_update():
    id_ = request.form['id']
    nama = request.form['nama_dokumen']
    kategori = request.form['kategori']
    file = request.files.get('file_dok')
    if file and file.filename != '':
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT file_path FROM dokumentasi WHERE id=%s", (id_,))
        old = cursor.fetchone()
        if old and old['file_path']:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'dokumentasi', old['file_path'])
            if os.path.exists(old_path):
                os.remove(old_path)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'dokumentasi', filename))
        cursor.execute("UPDATE dokumentasi SET nama_dokumen=%s, kategori=%s, file_path=%s WHERE id=%s", (nama, kategori, filename, id_))
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE dokumentasi SET nama_dokumen=%s, kategori=%s WHERE id=%s", (nama, kategori, id_))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/admin/dokumentasi/delete', methods=['POST'])
@login_required
def admin_dok_delete():
    id_ = request.form['id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT file_path FROM dokumentasi WHERE id=%s", (id_,))
    old = cursor.fetchone()
    if old and old['file_path']:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'dokumentasi', old['file_path'])
        if os.path.exists(old_path):
            os.remove(old_path)
    cursor.execute("DELETE FROM dokumentasi WHERE id=%s", (id_,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

# --- PENGADUAN ---
@app.route('/admin/pengaduan', methods=['GET'])
@login_required
def admin_pengaduan_list():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pengaduan ORDER BY created_at DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/admin/pengaduan/<int:id>', methods=['GET'])
@login_required
def admin_pengaduan_detail(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pengaduan WHERE id=%s", (id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/admin/pengaduan/update-status', methods=['POST'])
@login_required
def admin_pengaduan_status():
    id_ = request.form['id']
    status = request.form['status']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE pengaduan SET status=%s WHERE id=%s", (status, id_))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/admin/pengaduan/balas', methods=['POST'])
@login_required
def admin_pengaduan_balas():
    id_ = request.form['id']
    balasan = request.form['balasan']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE pengaduan SET balasan=%s WHERE id=%s", (balasan, id_))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/admin/pengaduan/delete', methods=['POST'])
@login_required
def admin_pengaduan_delete():
    id_ = request.form['id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT foto FROM pengaduan WHERE id=%s", (id_,))
    old = cursor.fetchone()
    if old and old['foto']:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'pengaduan', old['foto'])
        if os.path.exists(old_path):
            os.remove(old_path)
    cursor.execute("DELETE FROM pengaduan WHERE id=%s", (id_,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

# --- ADMIN CRUD ---
@app.route('/admin/admins', methods=['GET'])
@login_required
def admin_list():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, nama FROM admin")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/admin/admins/add', methods=['POST'])
@login_required
def admin_add():
    username = request.form['username']
    password = request.form['password']
    nama = request.form['nama']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admin (username, password, nama) VALUES (%s, %s, %s)", (username, password, nama))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/admin/admins/update', methods=['POST'])
@login_required
def admin_update():
    id_ = request.form['id']
    username = request.form['username']
    password = request.form['password']
    nama = request.form['nama']
    conn = get_db()
    cursor = conn.cursor()
    if password:
        cursor.execute("UPDATE admin SET username=%s, password=%s, nama=%s WHERE id=%s", (username, password, nama, id_))
    else:
        cursor.execute("UPDATE admin SET username=%s, nama=%s WHERE id=%s", (username, nama, id_))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/admin/admins/delete', methods=['POST'])
@login_required
def admin_delete():
    id_ = request.form['id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin WHERE id=%s", (id_,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

# ============================================
# Static file serving (optional, mainly for dev)
# ============================================
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
