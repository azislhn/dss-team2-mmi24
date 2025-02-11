import sqlite3

# Koneksi ke database
conn = sqlite3.connect("database.db")  # Sesuaikan dengan lokasi database jika tidak di folder yang sama
cursor = conn.cursor()

# Melihat semua tabel dalam database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Daftar Tabel:", tables)

# Menampilkan isi tabel 'prediksi'
cursor.execute("SELECT * FROM prediksi;")
rows = cursor.fetchall()
print("\nIsi Tabel Prediksi:")
for row in rows:
    print(row)

# Menampilkan isi tabel 'kriteria'
cursor.execute("SELECT * FROM kriteria;")
rows = cursor.fetchall()
print("\nIsi Tabel Kriteria:")
for row in rows:
    print(row)

# Menampilkan isi tabel 'alternatif'
cursor.execute("SELECT * FROM alternatif;")
rows = cursor.fetchall()
print("\nIsi Tabel Alternatif:")
for row in rows:
    print(row)

# Menampilkan isi tabel 'nilai_alternatif'
cursor.execute("SELECT * FROM nilai_alternatif;")
rows = cursor.fetchall()
print("\nIsi Tabel Nilai Alternatif:")
for row in rows:
    print(row)

# Tutup koneksi ke database
conn.close()
