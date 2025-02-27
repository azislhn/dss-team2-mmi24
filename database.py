import pymysql
import streamlit as st
import pandas as pd

class Database:
    def __init__(self, status=False):
        try:
            print("Not connected to database.")
            if status:
                print("Connecting database...")
                self.conn = pymysql.connect(
                    host=st.secrets.db_credentials.host,
                    user=st.secrets.db_credentials.user,
                    password=st.secrets.db_credentials.password,
                    database=st.secrets.db_credentials.database,
                    port=st.secrets.db_credentials.port,
                )
                self.cursor = self.conn.cursor()
                print("Database connected!")
                # self._drop_tables()
                # self._create_tables()
        except pymysql.MySQLError as err:
            print(f"Error: {err}")
            self.conn = None
            self.cursor = None

    def _create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS topik (
            id INT AUTO_INCREMENT PRIMARY KEY,
            judul VARCHAR(255),
            metode VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS kriteria (
            id INT AUTO_INCREMENT PRIMARY KEY,
            topik_id INT,
            nama VARCHAR(255),
            bobot FLOAT,
            tipe VARCHAR(50),
            FOREIGN KEY(topik_id) REFERENCES topik(id) ON DELETE CASCADE
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS subkriteria (
            id INT AUTO_INCREMENT PRIMARY KEY,
            kriteria_id INT,
            nama VARCHAR(255),
            bobot FLOAT,
            tipe VARCHAR(50),
            FOREIGN KEY(kriteria_id) REFERENCES kriteria(id) ON DELETE CASCADE
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS alternatif (
            id INT AUTO_INCREMENT PRIMARY KEY,
            topik_id INT,
            nama VARCHAR(255),
            FOREIGN KEY(topik_id) REFERENCES topik(id) ON DELETE CASCADE
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS nilai_alternatif (
            id INT AUTO_INCREMENT PRIMARY KEY,
            alternatif_id INT,
            kriteria_id INT,
            nilai FLOAT,
            FOREIGN KEY(alternatif_id) REFERENCES alternatif(id) ON DELETE CASCADE,
            FOREIGN KEY(kriteria_id) REFERENCES kriteria(id) ON DELETE CASCADE
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS subnilai_alternatif (
            id INT AUTO_INCREMENT PRIMARY KEY,
            alternatif_id INT,
            subkriteria_id INT,
            nilai FLOAT,
            FOREIGN KEY(alternatif_id) REFERENCES alternatif(id) ON DELETE CASCADE,
            FOREIGN KEY(subkriteria_id) REFERENCES subkriteria(id) ON DELETE CASCADE
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS hasil (
            id INT AUTO_INCREMENT PRIMARY KEY,
            topik_id INT,
            alternatif_id INT,
            skor FLOAT,
            FOREIGN KEY(topik_id) REFERENCES topik(id) ON DELETE CASCADE,
            FOREIGN KEY(alternatif_id) REFERENCES alternatif(id) ON DELETE CASCADE
        )''')
        
        print("Tabel selesai dibuat!")
        self.conn.commit()

    def _drop_tables(self, table=None):
        password_input = input("Password: ")
        correct_password = st.secrets.db_credentials.password

        if password_input == correct_password:
            confirm = input("Apakah Anda yakin ingin menghapus tabel? (y/n): ").strip().lower()
            if confirm == "y":
                if table is None:
                    tables = ["hasil", "subnilai_alternatif, ""nilai_alternatif", "alternatif", "subkriteria", "kriteria", "topik"]
                    for table in tables:
                        self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
                else:
                    self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
                self.conn.commit()
                print("Tabel berhasil dihapus.")
            else:
                print("Penghapusan tabel dibatalkan.")
        else:
            print("Password salah! Penghapusan tabel dibatalkan.")

    def simpan_topik(self, judul, metode):
        self.cursor.execute("INSERT INTO topik (judul, metode) VALUES (%s, %s)", (judul, metode))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_kriteria(self, topik_id, nama, bobot, tipe):
        self.cursor.execute("INSERT INTO kriteria (topik_id, nama, bobot, tipe) VALUES (%s, %s, %s, %s)", (topik_id, nama, float(bobot), tipe))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def simpan_subkriteria(self, kriteria_id, nama, bobot, tipe):
        self.cursor.execute("INSERT INTO subkriteria (kriteria_id, nama, bobot, tipe) VALUES (%s, %s, %s, %s)", (kriteria_id, nama, float(bobot), tipe))
        self.conn.commit()
        return self.cursor.lastrowid

    def simpan_alternatif(self, topik_id, nama):
        self.cursor.execute("INSERT INTO alternatif (topik_id, nama) VALUES (%s, %s)", (topik_id, nama))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def simpan_nilai_alternatif(self, alternatif_id, kriteria_id, nilai):
        self.cursor.execute("INSERT INTO nilai_alternatif (alternatif_id, kriteria_id, nilai) VALUES (%s, %s, %s)", (alternatif_id, kriteria_id, float(nilai)))
        self.conn.commit()
        
    def simpan_subnilai_alternatif(self, alternatif_id, subkriteria_id, nilai):
        self.cursor.execute("INSERT INTO subnilai_alternatif (alternatif_id, subkriteria_id, nilai) VALUES (%s, %s, %s)", (alternatif_id, subkriteria_id, float(nilai)))
        self.conn.commit()
    
    def simpan_hasil(self, topik_id, alternatif_id, skor):
        self.cursor.execute("INSERT INTO hasil (topik_id, alternatif_id, skor) VALUES (%s, %s, %s)", (topik_id, alternatif_id, float(skor)))
        self.conn.commit()

    def ambil_topik(self):
        self.cursor.execute("SELECT * FROM topik ORDER BY timestamp DESC, id DESC;")
        return self.cursor.fetchall()
    
    def ambil_kriteria(self, topik_id):
        self.cursor.execute("SELECT * FROM kriteria WHERE topik_id = %s", (topik_id,))
        return self.cursor.fetchall()
    
    def ambil_subkriteria(self, kriteria_id):
        self.cursor.execute("SELECT * FROM subkriteria WHERE kriteria_id = %s", (kriteria_id,))
        return self.cursor.fetchall()
    
    def ambil_alternatif(self, topik_id):
        self.cursor.execute("SELECT * FROM alternatif WHERE topik_id = %s", (topik_id,))
        return self.cursor.fetchall()

    def ambil_nilai_alternatif(self, topik_id):
        self.cursor.execute("SELECT nilai_alternatif.* FROM nilai_alternatif JOIN alternatif ON nilai_alternatif.alternatif_id = alternatif.id WHERE alternatif.topik_id = %s", (topik_id,))
        return self.cursor.fetchall()

    def ambil_subnilai_alternatif(self, topik_id):
        query = """
        SELECT ns.*, s.kriteria_id FROM subnilai_alternatif ns
        JOIN subkriteria s ON ns.subkriteria_id = s.id
        JOIN alternatif a ON ns.alternatif_id = a.id
        WHERE a.topik_id = %s;
        """
        self.cursor.execute(query, (topik_id,))
        return self.cursor.fetchall()
    
    def ambil_hasil(self, topik_id):
        self.cursor.execute("SELECT a.nama, h.skor FROM hasil h JOIN alternatif a ON h.alternatif_id = a.id WHERE h.topik_id = %s", (topik_id,))
        return self.cursor.fetchall()
    
    def ambil_pivot_kriteria(self, topik_id):
        query = """
            SELECT 
                k.id AS kriteria_id, 
                k.nama AS kriteria_nama, 
                k.bobot AS bobot_kriteria, 
                k.tipe AS tipe_kriteria,
                COALESCE(s.id, 0) AS subkriteria_id, 
                COALESCE(s.nama, '-') AS subkriteria_nama, 
                COALESCE(s.bobot, 0) AS bobot_subkriteria, 
                COALESCE(s.tipe, k.tipe) AS tipe_subkriteria
            FROM kriteria k
            LEFT JOIN subkriteria s ON k.id = s.kriteria_id
            WHERE k.topik_id = %s
        """
        self.cursor.execute(query, (topik_id,))
        data = self.cursor.fetchall()

        df = pd.DataFrame(data, columns=[
            "kriteria_id", "kriteria_nama", "bobot_kriteria", "tipe_kriteria",
            "subkriteria_id", "subkriteria_nama", "bobot_subkriteria", "tipe_subkriteria"
        ])

        final_data = []
        for _, row in df.iterrows():
            final_data.append({
                "Kriteria/Subkriteria": row["kriteria_nama"],
                "Bobot": row["bobot_kriteria"],
                "Tipe Kriteria": row["tipe_kriteria"]
            })
            # Tambahkan subkriteria jika ada
            if row["subkriteria_id"] != 0:
                final_data.append({
                    "Kriteria/Subkriteria": f"{row['kriteria_nama']} ({row['subkriteria_nama']})",
                    "Bobot": row["bobot_subkriteria"],
                    "Tipe Kriteria": row["tipe_subkriteria"]
                })

        kriteria_df = pd.DataFrame(final_data).drop_duplicates()
        return kriteria_df


    def ambil_pivot_data(self, topik_id):
        query = """
            SELECT 
                a.id AS alternatif_id, 
                a.nama AS alternatif_nama, 
                h.skor AS hasil,
                k.id AS kriteria_id, 
                k.nama AS kriteria_nama, 
                COALESCE(s.id, 0) AS subkriteria_id, 
                COALESCE(s.nama, '-') AS subkriteria_nama, 
                COALESCE(ns.nilai, -1) AS subnilai_alternatif, 
                COALESCE(na.nilai, -1) AS nilai_alternatif
            FROM alternatif a
            LEFT JOIN hasil h ON a.id = h.alternatif_id
            LEFT JOIN kriteria k ON k.topik_id = a.topik_id
            LEFT JOIN nilai_alternatif na ON a.id = na.alternatif_id AND na.kriteria_id = k.id
            LEFT JOIN subkriteria s ON s.kriteria_id = k.id
            LEFT JOIN subnilai_alternatif ns ON a.id = ns.alternatif_id AND ns.subkriteria_id = s.id
            WHERE a.topik_id = %s
            ORDER BY a.id, k.id, s.id;
        """
        
        self.cursor.execute(query, (topik_id,))
        data = self.cursor.fetchall()

        df = pd.DataFrame(data, columns=[
        "alternatif_id", "alternatif_nama", "hasil", 
        "kriteria_id", "kriteria_nama", 
        "subkriteria_id", "subkriteria_nama", 
        "subnilai_alternatif", "nilai_alternatif"
        ])
        df["kolom_kriteria"] = df.apply(
            lambda x: f"{x['kriteria_nama']} ({x['subkriteria_nama']})" if x["subkriteria_id"] != 0 else x["kriteria_nama"], axis=1
        )
        df["nilai_akhir"] = df.apply(
            lambda x: x["subnilai_alternatif"] if x["subkriteria_id"] != 0 else x["nilai_alternatif"], axis=1
        )

        pivot_df = df.pivot_table(
            index="alternatif_id",  
            columns="kolom_kriteria",  
            values="nilai_akhir",  
            aggfunc="first" 
        )
        hasil_df = df[["alternatif_id", "alternatif_nama", "hasil"]].drop_duplicates().set_index("alternatif_id")
        pivot_df = hasil_df.join(pivot_df)
        pivot_df["Rank"] = pivot_df["hasil"].rank(method="dense", ascending=False).astype(int)
        pivot_df = pivot_df.rename(columns={"hasil": "Skor Hasil Perhitungan", "alternatif_nama": "Alternatif"})
        pivot_df = pivot_df.sort_values(by="Rank").set_index("Rank")
        return pivot_df
    
    def hapus_topik(self, topik_id):
        try:
            self.cursor.execute("DELETE FROM topik WHERE id = %s", (topik_id,))
            self.conn.commit()
            print(f"topik dengan ID {topik_id} dan semua relasi telah dihapus.")
        except pymysql.MySQLError as err:
            print(f"Error: {err}")

    def close_connection(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("Koneksi database ditutup.")
