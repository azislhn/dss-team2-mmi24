import numpy as np

# 1. Fungsi Perhitungan SAW
def normalisasi_saw(matrix, tipe_kriteria):
    matrix = np.array(matrix, dtype=np.float64)
    norm_matrix = np.zeros_like(matrix)

    for j in range(matrix.shape[1]):
        if tipe_kriteria[j] == "benefit":
            norm_matrix[:, j] = matrix[:, j] / np.max(matrix[:, j])
        else:  # cost
            norm_matrix[:, j] = np.min(matrix[:, j]) / matrix[:, j]
    
    return norm_matrix

def hitung_saw(matrix, bobot, tipe_kriteria):
    norm_matrix = normalisasi_saw(matrix, tipe_kriteria)
    hasil = np.sum(norm_matrix * bobot, axis=1)
    return hasil

# 2. Fungsi Perhitungan WP
def hitung_wp(matrix, bobot, tipe_kriteria):
    matrix = np.array(matrix, dtype=np.float64)
    bobot = np.array(bobot)
    
    # Normalisasi untuk benefit/cost
    for j in range(matrix.shape[1]):
        if tipe_kriteria[j] == "cost":
            matrix[:, j] = 1 / matrix[:, j]  # Cost dibalik
    
    # Perhitungan WP
    hasil = np.prod(matrix ** bobot, axis=1)
    return hasil

# 3. Fungsi Perhitungan TOPSIS
def hitung_topsis(matrix, bobot, tipe_kriteria):
    matrix = np.array(matrix, dtype=np.float64)
    bobot = np.array(bobot)
    
    # Normalisasi Matriks
    norm_matrix = matrix / np.sqrt(np.sum(matrix ** 2, axis=0))

    # Pembobotan
    weighted_matrix = norm_matrix * bobot

    # Menentukan solusi ideal positif dan negatif
    ideal_positif = np.max(weighted_matrix, axis=0) if "benefit" else np.min(weighted_matrix, axis=0)
    ideal_negatif = np.min(weighted_matrix, axis=0) if "cost" else np.max(weighted_matrix, axis=0)
    
    ideal_positif = np.array([np.max(weighted_matrix[:, j]) if tipe_kriteria[j] == "benefit" else np.min(weighted_matrix[:, j]) for j in range(weighted_matrix.shape[1])])
    ideal_negatif = np.array([np.min(weighted_matrix[:, j]) if tipe_kriteria[j] == "benefit" else np.max(weighted_matrix[:, j]) for j in range(weighted_matrix.shape[1])])


    # Jarak ke solusi ideal positif & negatif
    jarak_positif = np.sqrt(np.sum((weighted_matrix - ideal_positif) ** 2, axis=1))
    jarak_negatif = np.sqrt(np.sum((weighted_matrix - ideal_negatif) ** 2, axis=1))

    # Menghitung skor preferensi
    hasil = jarak_negatif / (jarak_positif + jarak_negatif)
    return hasil

def hitung_topsis(matrix, bobot, tipe_kriteria):
    matrix = np.array(matrix, dtype=np.float64)
    bobot = np.array(bobot)
    
    # Normalisasi matriks
    norm_matrix = matrix / np.sqrt(np.sum(matrix ** 2, axis=0))
    
    # Pembobotan matriks
    weighted_matrix = norm_matrix * bobot
    
    # Menentukan solusi ideal positif dan negatif
    ideal_positif = np.array([np.max(weighted_matrix[:, j]) if tipe_kriteria[j] == "benefit" else np.min(weighted_matrix[:, j]) for j in range(weighted_matrix.shape[1])])
    ideal_negatif = np.array([np.min(weighted_matrix[:, j]) if tipe_kriteria[j] == "benefit" else np.max(weighted_matrix[:, j]) for j in range(weighted_matrix.shape[1])])
    
    # Menghitung jarak solusi ideal positif dan negatif
    jarak_positif = np.sqrt(np.sum((weighted_matrix - ideal_positif) ** 2, axis=1))
    jarak_negatif = np.sqrt(np.sum((weighted_matrix - ideal_negatif) ** 2, axis=1))
    
    # Menghitung skor preferensi
    hasil = jarak_negatif / (jarak_positif + jarak_negatif)
    
    return hasil