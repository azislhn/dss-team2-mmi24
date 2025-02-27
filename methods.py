import numpy as np

def simpan_ke_database(db, topik, metode, kriteria, subkriteria, alternatif, nilai, subnilai, hasil):
    topik_id = db.simpan_topik(topik, metode)
    kriteria_ids = [db.simpan_kriteria(topik_id, k["Nama"], k["Bobot"], k["Tipe"]) for k in kriteria]
    alternatif_ids = [db.simpan_alternatif(topik_id, a["Nama"]) for a in alternatif]

    subkriteria_ids = []
    for i, k in enumerate(kriteria):
        if subkriteria and k["Nama"] in subkriteria:
            data = subkriteria[k["Nama"]]
            for d in data:
                id = db.simpan_subkriteria(kriteria_ids[i], d["Nama"], d["Bobot"], d["Tipe"])
                subkriteria_ids.append(id)
    
    for i, a_id in enumerate(alternatif_ids):
        for j, k_id in enumerate(kriteria_ids):
            db.simpan_nilai_alternatif(a_id, k_id, nilai[i][j])
        for n, s_id in enumerate(subkriteria_ids):
            db.simpan_subnilai_alternatif(a_id, s_id, subnilai[i][n])
        db.simpan_hasil(topik_id, a_id, hasil[i])

def normalisasi_bobot_kriteria(kriteria, subkriteria=None):
    bobot = np.array([k["Bobot"] for k in kriteria])
    norm_bobot = bobot / np.sum(bobot)
    new_kriteria_data = [] 
    for i, k in enumerate(kriteria):
        if subkriteria and k["Subkriteria"] > 0 and k["Nama"] in subkriteria:
            data = subkriteria[k["Nama"]]
            sub_bobot = np.array([d["Bobot"] for d in data])
            norm_sub_bobot = sub_bobot / np.sum(sub_bobot)
            new_kriteria_data.extend({
                "Nama": d["Nama"],
                "Bobot": norm_sub_bobot[j] * norm_bobot[i],
                "Tipe": d["Tipe"]
            } for j, d in enumerate(data))
        else:
            new_kriteria_data.append({
                "Nama": k["Nama"],
                "Bobot": norm_bobot[i],
                "Tipe": k["Tipe"]
            })
    return new_kriteria_data

def hitung_saw(matrix, kriteria):
    matrix = np.array(matrix, dtype=np.float64)
    norm_matrix = np.zeros_like(matrix)
    bobot = [k["Bobot"] for k in kriteria]
    tipe = [k["Tipe"] for k in kriteria]

    for j in range(matrix.shape[1]):
        if tipe[j] == "benefit":
            norm_matrix[:, j] = matrix[:, j] / np.max(matrix[:, j])
        elif tipe[j] == "cost":
            norm_matrix[:, j] = np.min(matrix[:, j]) / matrix[:, j]
    
    hasil = np.sum(norm_matrix * bobot, axis=1)
    return hasil

def hitung_wp(matrix, kriteria):
    matrix = np.array(matrix, dtype=np.float64)
    bobot = [k["Bobot"] for k in kriteria]
    tipe = [k["Tipe"] for k in kriteria]
    
    for j in range(matrix.shape[1]):
        if tipe[j] == "cost":
            matrix[:, j] = 1 / matrix[:, j]  # Cost dibalik
    
    hasil = np.prod(matrix ** bobot, axis=1)
    return hasil

def hitung_topsis(matrix, kriteria):
    matrix = np.array(matrix, dtype=np.float64)
    norm_matrix = matrix / np.sqrt(np.sum(matrix ** 2, axis=0))
    bobot = [k["Bobot"] for k in kriteria]
    tipe = [k["Tipe"] for k in kriteria]
    weighted_matrix = norm_matrix * bobot    
    # ideal_positif = np.where(tipe == "benefit", np.max(weighted_matrix, axis=0), np.min(weighted_matrix, axis=0))
    # ideal_negatif = np.where(tipe == "benefit", np.min(weighted_matrix, axis=0), np.max(weighted_matrix, axis=0))
    ideal_positif = np.array([
        np.max(weighted_matrix[:, i]) if tipe[i] == "benefit" else np.min(weighted_matrix[:, i]) 
        for i in range(len(tipe))
    ])
    ideal_negatif = np.array([
        np.min(weighted_matrix[:, i]) if tipe[i] == "benefit" else np.max(weighted_matrix[:, i]) 
        for i in range(len(tipe))
    ])
    jarak_positif = np.sqrt(np.sum((weighted_matrix - ideal_positif) ** 2, axis=1))
    jarak_negatif = np.sqrt(np.sum((weighted_matrix - ideal_negatif) ** 2, axis=1))
    hasil = jarak_negatif / (jarak_positif + jarak_negatif)
    return hasil