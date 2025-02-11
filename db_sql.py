import sqlite3
import os

class Database:
    def __init__(self, db_path="database.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS prediksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_prediksi TEXT,
            metode TEXT
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS kriteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediksi_id INTEGER,
            nama TEXT,
            tipe TEXT,
            bobot REAL,
            FOREIGN KEY(prediksi_id) REFERENCES prediksi(id)
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS alternatif (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediksi_id INTEGER,
            nama TEXT,
            FOREIGN KEY(prediksi_id) REFERENCES prediksi(id)
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS nilai_alternatif (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alternatif_id INTEGER,
            kriteria_id INTEGER,
            nilai REAL,
            FOREIGN KEY(alternatif_id) REFERENCES alternatif(id),
            FOREIGN KEY(kriteria_id) REFERENCES kriteria(id)
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS hasil (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediksi_id INTEGER,
            alternatif_id INTEGER,
            skor REAL,
            FOREIGN KEY(prediksi_id) REFERENCES prediksi(id),
            FOREIGN KEY(alternatif_id) REFERENCES alternatif(id)
        )''')
        
        self.conn.commit()

    def simpan_prediksi(self, nama_prediksi, metode):
        self.cursor.execute("INSERT INTO prediksi (nama_prediksi, metode) VALUES (?, ?)", (nama_prediksi, metode))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_kriteria(self, prediksi_id, nama, tipe, bobot):
        self.cursor.execute("INSERT INTO kriteria (prediksi_id, nama, tipe, bobot) VALUES (?, ?, ?, ?)", (prediksi_id, nama, tipe, bobot))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_alternatif(self, prediksi_id, nama):
        self.cursor.execute("INSERT INTO alternatif (prediksi_id, nama) VALUES (?, ?)", (prediksi_id, nama))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_nilai_alternatif(self, alternatif_id, kriteria_id, nilai):
        self.cursor.execute("INSERT INTO nilai_alternatif (alternatif_id, kriteria_id, nilai) VALUES (?, ?, ?)", (alternatif_id, kriteria_id, nilai))
        self.conn.commit()
    
    def simpan_hasil(self, prediksi_id, alternatif_id, skor):
        self.cursor.execute("INSERT INTO hasil (prediksi_id, alternatif_id, skor) VALUES (?, ?, ?)", (prediksi_id, alternatif_id, skor))
        self.conn.commit()

    def ambil_prediksi(self):
        self.cursor.execute("SELECT * FROM prediksi")
        return self.cursor.fetchall()
    
    def ambil_kriteria(self, prediksi_id):
        self.cursor.execute("SELECT * FROM kriteria WHERE prediksi_id = ?", (prediksi_id,))
        return self.cursor.fetchall()
    
    def ambil_alternatif(self, prediksi_id):
        self.cursor.execute("SELECT * FROM alternatif WHERE prediksi_id = ?", (prediksi_id,))
        return self.cursor.fetchall()
    
    def ambil_nilai_alternatif(self, prediksi_id):
        self.cursor.execute("SELECT nilai_alternatif.* FROM nilai_alternatif JOIN alternatif ON nilai_alternatif.alternatif_id = alternatif.id WHERE alternatif.prediksi_id = ?", (prediksi_id,))
        return self.cursor.fetchall()
    
    def ambil_hasil(self, prediksi_id):
        self.cursor.execute("SELECT hasil.* FROM hasil WHERE prediksi_id = ?", (prediksi_id,))
        return self.cursor.fetchall()
    
    def close_connection(self):
        self.conn.close()
