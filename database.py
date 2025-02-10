import firebase_admin
import os
import logging
from firebase_admin import credentials, firestore

# Cek apakah kredensial Firebase tersedia
if os.path.exists("path/to/your/firebase-credentials.json"):
    try:
        cred = credentials.Certificate("path/to/your/firebase-credentials.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        logging.warning(f"Firebase tidak dapat diinisialisasi: {e}")
        db = None
else:
    logging.warning("Firebase kredensial tidak ditemukan, melewati inisialisasi.")
    db = None

class Database:
    def __init__(self):
        self.db = db

    def is_connected(self):
        return self.db is not None

    def simpan_prediksi(self, nama_prediksi, metode):
        if not self.is_connected():
            return None
        doc_ref = self.db.collection("prediksi").add({
            "nama_prediksi": nama_prediksi,
            "metode": metode
        })
        return doc_ref[1].id

    def simpan_kriteria(self, prediksi_id, nama, tipe, bobot):
        if not self.is_connected():
            return None
        doc_ref = self.db.collection("prediksi").document(prediksi_id).collection("kriteria").add({
            "nama": nama,
            "tipe": tipe,
            "bobot": bobot
        })
        return doc_ref[1].id

    def simpan_alternatif(self, prediksi_id, nama):
        if not self.is_connected():
            return None
        doc_ref = self.db.collection("prediksi").document(prediksi_id).collection("alternatif").add({
            "nama": nama
        })
        return doc_ref[1].id

    def simpan_nilai_alternatif(self, alternatif_id, kriteria_id, nilai):
        if not self.is_connected():
            return
        self.db.collection("nilai_alternatif").add({
            "alternatif_id": alternatif_id,
            "kriteria_id": kriteria_id,
            "nilai": nilai
        })

    def simpan_nilai_normalisasi(self, alternatif_id, kriteria_id, nilai):
        if not self.is_connected():
            return
        self.db.collection("nilai_normalisasi").add({
            "alternatif_id": alternatif_id,
            "kriteria_id": kriteria_id,
            "nilai": nilai
        })
    
    def simpan_nilai_pembobotan(self, alternatif_id, kriteria_id, nilai):
        if not self.is_connected():
            return
        self.db.collection("nilai_pembobotan").add({
            "alternatif_id": alternatif_id,
            "kriteria_id": kriteria_id,
            "nilai": nilai
        })

    def simpan_hasil(self, prediksi_id, alternatif_id, skor):
        if not self.is_connected():
            return
        self.db.collection("prediksi").document(prediksi_id).collection("hasil").add({
            "alternatif_id": alternatif_id,
            "skor": skor
        })
