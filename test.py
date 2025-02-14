from models import hitung_topsis
import numpy as np
from database import Database

db = Database()

# Contoh Data dari Materi (Contoh 1: Memilih Mobil)
matrix = [
    [7, 9, 9, 8],  # Civic
    [8, 7, 8, 7],  # Saturn
    [9, 6, 8, 9],  # Ford
    [6, 7, 8, 6],  # Mazda
]

criteria_names = ['Style', 'Reliability', 'Fuel Eco', 'Cost']
criteria_weights = [0.10, 0.40, 0.30, 0.20]
criteria_types = ["benefit", "benefit", "benefit", "cost"]

alternatives = ["Civic", "Saturn", "Ford", "Mazda"]

# Hitung TOPSIS
criteria_data = np.array(list(zip(criteria_names, criteria_types, criteria_weights)), dtype=object)

matrix_np = np.array(matrix)
bobot_np = np.array(criteria_weights)
tipe_kriteria = np.array(criteria_types)

scores = hitung_topsis(matrix_np, bobot_np, tipe_kriteria)

def storing():
    print('\nscores', scores)

    print(criteria_data)
    print(alternatives)
    print(matrix)
    # Simpan Hasil
    prediksi_id = db.simpan_prediksi("Memilih Mobil", "TOPSIS")
    kriteria_ids = [db.simpan_kriteria(prediksi_id, k[0], k[1], k[2]) for k in criteria_data]
    alternatif_ids = [db.simpan_alternatif(prediksi_id, a) for a in alternatives]
    
    print('prediksi_id', prediksi_id)

    for i, alternatif_id in enumerate(alternatif_ids):
        for j, kriteria_id in enumerate(kriteria_ids):
            db.simpan_nilai_alternatif(alternatif_id, kriteria_id, matrix[i][j])

    hasil_sorted = sorted(zip(alternatif_ids, alternatives, scores), key=lambda x: x[2], reverse=True)
    for alt_id, alt, skor in hasil_sorted:
        db.simpan_hasil(prediksi_id, alt_id, skor)


def delete(id):
    db.hapus_prediksi(id)
    return


