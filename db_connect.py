import mysql.connector
import os

class Database:
    def __init__(self, host="localhost", user="root", password="", database="dss_saw_wp_topsis"):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS prediksi (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nama_prediksi VARCHAR(255),
            metode VARCHAR(255)
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS kriteria (
            id INT AUTO_INCREMENT PRIMARY KEY,
            prediksi_id INT,
            nama VARCHAR(255),
            tipe VARCHAR(50),
            bobot FLOAT,
            FOREIGN KEY(prediksi_id) REFERENCES prediksi(id) ON DELETE CASCADE
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS alternatif (
            id INT AUTO_INCREMENT PRIMARY KEY,
            prediksi_id INT,
            nama VARCHAR(255),
            FOREIGN KEY(prediksi_id) REFERENCES prediksi(id) ON DELETE CASCADE
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS nilai_alternatif (
            id INT AUTO_INCREMENT PRIMARY KEY,
            alternatif_id INT,
            kriteria_id INT,
            nilai FLOAT,
            FOREIGN KEY(alternatif_id) REFERENCES alternatif(id) ON DELETE CASCADE,
            FOREIGN KEY(kriteria_id) REFERENCES kriteria(id) ON DELETE CASCADE
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS hasil (
            id INT AUTO_INCREMENT PRIMARY KEY,
            prediksi_id INT,
            alternatif_id INT,
            skor FLOAT,
            FOREIGN KEY(prediksi_id) REFERENCES prediksi(id) ON DELETE CASCADE,
            FOREIGN KEY(alternatif_id) REFERENCES alternatif(id) ON DELETE CASCADE
        )''')
        
        self.conn.commit()

    def simpan_prediksi(self, nama_prediksi, metode):
        self.cursor.execute("INSERT INTO prediksi (nama_prediksi, metode) VALUES (%s, %s)", (nama_prediksi, metode))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_kriteria(self, prediksi_id, nama, tipe, bobot):
        self.cursor.execute("INSERT INTO kriteria (prediksi_id, nama, tipe, bobot) VALUES (%s, %s, %s, %s)", (prediksi_id, nama, tipe, bobot))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_alternatif(self, prediksi_id, nama):
        self.cursor.execute("INSERT INTO alternatif (prediksi_id, nama) VALUES (%s, %s)", (prediksi_id, nama))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_nilai_alternatif(self, alternatif_id, kriteria_id, nilai):
        self.cursor.execute("INSERT INTO nilai_alternatif (alternatif_id, kriteria_id, nilai) VALUES (%s, %s, %s)", (alternatif_id, kriteria_id, nilai))
        self.conn.commit()
    
    def simpan_hasil(self, prediksi_id, alternatif_id, skor):
        self.cursor.execute("INSERT INTO hasil (prediksi_id, alternatif_id, skor) VALUES (%s, %s, %s)", (prediksi_id, alternatif_id, skor))
        self.conn.commit()

    def ambil_prediksi(self):
        self.cursor.execute("SELECT * FROM prediksi")
        return self.cursor.fetchall()
    
    def ambil_kriteria(self, prediksi_id):
        self.cursor.execute("SELECT * FROM kriteria WHERE prediksi_id = %s", (prediksi_id,))
        return self.cursor.fetchall()
    
    def ambil_alternatif(self, prediksi_id):
        self.cursor.execute("SELECT * FROM alternatif WHERE prediksi_id = %s", (prediksi_id,))
        return self.cursor.fetchall()
    
    def ambil_nilai_alternatif(self, prediksi_id):
        self.cursor.execute("SELECT nilai_alternatif.* FROM nilai_alternatif JOIN alternatif ON nilai_alternatif.alternatif_id = alternatif.id WHERE alternatif.prediksi_id = %s", (prediksi_id,))
        return self.cursor.fetchall()
    
    def ambil_hasil(self, prediksi_id):
        self.cursor.execute("SELECT hasil.* FROM hasil WHERE prediksi_id = %s", (prediksi_id,))
        return self.cursor.fetchall()
    
    def close_connection(self):
        self.conn.close()
