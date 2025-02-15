# import mysql.connector
import pymysql
import streamlit as st

class Database:
    def __init__(self, host=st.secrets.db_credentials.host, user=st.secrets.db_credentials.user, password=st.secrets.db_credentials.password, database=st.secrets.db_credentials.database, port=st.secrets.db_credentials.port):
        try:
            print("Connecting database...")
            self.conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                # cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
            print("Database connected!")
            # self._create_tables()
        except pymysql.MySQLError as err:
            print(f"Error: {err}")
            self.conn = None
            self.cursor = None

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

    def _drop_tables(self):
        password_input = input("Password: ")
        correct_password = "BidvozghXocWEgDjBxvHoOFgjAPoRnqM"

        if password_input == correct_password:
            confirm = input("Apakah Anda yakin ingin menghapus semua tabel? (y/n): ").strip().lower()
            if confirm == "y":
                tables = ["hasil", "nilai_alternatif", "alternatif", "kriteria", "prediksi"]
                for table in tables:
                    self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
                self.conn.commit()
                print("Semua tabel berhasil dihapus.")
            else:
                print("Penghapusan tabel dibatalkan.")
        else:
            print("Password salah! Penghapusan tabel dibatalkan.")
    
    def simpan_prediksi(self, nama_prediksi, metode):
        self.cursor.execute("INSERT INTO prediksi (nama_prediksi, metode) VALUES (%s, %s)", (nama_prediksi, metode))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_kriteria(self, prediksi_id, nama, tipe, bobot):
        self.cursor.execute("INSERT INTO kriteria (prediksi_id, nama, tipe, bobot) VALUES (%s, %s, %s, %s)", (prediksi_id, nama, tipe, float(bobot)))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_alternatif(self, prediksi_id, nama):
        self.cursor.execute("INSERT INTO alternatif (prediksi_id, nama) VALUES (%s, %s)", (prediksi_id, nama))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_nilai_alternatif(self, alternatif_id, kriteria_id, nilai):
        self.cursor.execute("INSERT INTO nilai_alternatif (alternatif_id, kriteria_id, nilai) VALUES (%s, %s, %s)", (alternatif_id, kriteria_id, float(nilai)))
        self.conn.commit()
    
    def simpan_hasil(self, prediksi_id, alternatif_id, skor):
        self.cursor.execute("INSERT INTO hasil (prediksi_id, alternatif_id, skor) VALUES (%s, %s, %s)", (prediksi_id, alternatif_id, float(skor)))
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
        # self.cursor.execute("SELECT hasil.* FROM hasil WHERE prediksi_id = %s", (prediksi_id,))
        self.cursor.execute("SELECT a.nama, h.skor FROM hasil h JOIN alternatif a ON h.alternatif_id = a.id WHERE h.prediksi_id = %s", (prediksi_id,))
        return self.cursor.fetchall()
    
    def hapus_prediksi(self, prediksi_id):
        try:
            self.cursor.execute("DELETE FROM prediksi WHERE id = %s", (prediksi_id,))
            self.conn.commit()
            print(f"Prediksi dengan ID {prediksi_id} dan semua relasi telah dihapus.")
        except pymysql.MySQLError as err:
            print(f"Error: {err}")

    def close_connection(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("Koneksi database ditutup.")