import streamlit as st
import numpy as np
import pandas as pd
from database import Database
from models import hitung_saw, hitung_wp, hitung_topsis

# Debugging Mode
import traceback

db = Database()

st.set_page_config(page_title="DSS Framework", layout="centered")
st.title("Sistem Pendukung Pembuatan Keputusan - SAW, WP, TOPSIS")

# Sidebar 
st.sidebar.markdown("### DSS Framework")
st.sidebar.markdown("### Menu Navigasi")
menu = st.sidebar.radio("Pilih Halaman", ["🏠 Input Data", "📜 Riwayat"])
st.sidebar.markdown("---")
st.sidebar.text("Dikembangkan oleh:")
st.sidebar.text("Aziz Solihin, Firda Ayu Safitri, Kadek Gunamulya Sudarma Yasa")
st.sidebar.text("MMI24 UGM")

if menu == "🏠 Input Data":
    st.subheader("Masukkan Data")
    nama_prediksi = st.text_input("Nama Topik", "")
    metode = st.selectbox("Pilih Metode", ["SAW", "WP", "TOPSIS"])
    jumlah_kriteria = st.number_input("Jumlah Kriteria", min_value=1, step=1, value=3)
    jumlah_alternatif = st.number_input("Jumlah Alternatif", min_value=1, step=1, value=3)
    update_button = st.button("Perbarui")
    
    if update_button:
        if not nama_prediksi.strip():
            st.error("Nama topik harus diisi.")

    tab_kriteria, tab_alternatif = st.tabs(["**Kriteria**", "**Alternatif**"])
    
    with tab_kriteria:
        st.subheader("Kriteria")
        kriteria_data = []
        for i in range(jumlah_kriteria):
            nama = st.text_input(f"Nama Kriteria {i+1}", key=f"kriteria_{i}")
            col1, col2 = st.columns(2)
            with col1:
                tipe = st.radio(f"Tipe {i+1}", ["benefit", "cost"], key=f"tipe_{i}")
            with col2:
                if metode == "WP":
                    bobot = st.number_input(f"Bobot {i+1}", 0.0, 100.0, step=1.0, key=f"bobot_{i}")
                else:
                    bobot = st.number_input(f"Bobot {i+1}", 0.0, 1.0, step=0.05, key=f"bobot_{i}")
            kriteria_data.append([nama, tipe, bobot])
            st.markdown("---")
    
    with tab_alternatif:
        st.subheader("Alternatif")
        alternatif_data = []
        matrix_data = []
        for i in range(jumlah_alternatif):
            nama = st.text_input(f"Alternatif {i+1}", key=f"alt_{i}")
            nilai = [st.number_input(f"{nama} - {kriteria_data[j][0]}", min_value=0.0, key=f"nilai_{i}_{j}") for j in range(jumlah_kriteria)]
            alternatif_data.append(nama)
            matrix_data.append(nilai)
            st.markdown("---")
    
    submit = st.button(f"Simpan & Hitung dengan {metode}")
    
    if submit:
        # Validasi input
        if not nama_prediksi.strip():
            st.error("Nama prediksi harus diisi.")
        elif not all(k[0].strip() for k in kriteria_data):
            st.error("Semua nama kriteria harus diisi.")
        elif not all(alternatif_data) or not all(a.strip() for a in alternatif_data):
            st.error("Semua nama alternatif harus diisi.")
        elif not all(all(row) for row in matrix_data):
            st.error("Semua nilai alternatif harus diisi.")
        else:
            try:
                matrix_np = np.array(matrix_data)
                bobot_np = np.array([k[2] for k in kriteria_data])
                tipe_kriteria = np.array([k[1] for k in kriteria_data])
                
                hasil = None
                if metode == "SAW":
                    hasil = hitung_saw(matrix_np, bobot_np, tipe_kriteria)
                elif metode == "WP":
                    hasil = hitung_wp(matrix_np, bobot_np, tipe_kriteria)
                elif metode == "TOPSIS":
                    hasil = hitung_topsis(matrix_np, bobot_np, tipe_kriteria)

                # Simpan ke database
                if hasil is not None:
                    with st.status("Sedang memproses...") as status:

                        prediksi_id = db.simpan_prediksi(nama_prediksi, metode)
                        kriteria_ids = [db.simpan_kriteria(prediksi_id, k[0], k[1], k[2]) for k in kriteria_data]
                        alternatif_ids = [db.simpan_alternatif(prediksi_id, a) for a in alternatif_data]

                        for i, alternatif_id in enumerate(alternatif_ids):
                            for j, kriteria_id in enumerate(kriteria_ids):
                                db.simpan_nilai_alternatif(alternatif_id, kriteria_id, matrix_data[i][j])
                        
                        hasil_sorted = sorted(zip(alternatif_ids, alternatif_data, hasil), key=lambda x: x[2], reverse=True)
                        
                        for alt_id, alt, skor in hasil_sorted:
                            db.simpan_hasil(prediksi_id, alt_id, skor)
                        
                        status.update(label="Berhasil menghitung!", state="complete")
                    
                    df_hasil = pd.DataFrame({
                        "Alternatif": [h[1] for h in hasil_sorted],
                        "Skor": [h[2] for h in hasil_sorted]
                    })
                    st.dataframe(df_hasil, hide_index=True, use_container_width=True)
                else:
                    st.error("Terjadi kesalahan saat menghitung.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
                st.text(traceback.format_exc())

elif menu == "📜 Riwayat":
    st.subheader("Riwayat Proses")
    search_query = st.text_input("Cari Berdasarkan Topik")
    if db is None:
        st.error("Koneksi ke database gagal.")
    else:
        prediksi_tersimpan = db.ambil_prediksi()

        if prediksi_tersimpan:
            for prediksi in prediksi_tersimpan:
                prediksi_id, nama_prediksi, metode, timestamp = prediksi

                if search_query.lower() in nama_prediksi.lower():
                    st.write(f"### Topik: {nama_prediksi}")
                    st.write(f"Metode: {metode}")
                    
                    # Ambil hasil perhitungan
                    hasil_tersimpan = db.ambil_semua_data_keputusan(prediksi_id)
                    st.write("#### Hasil Perhitungan")

                    df = pd.DataFrame(hasil_tersimpan, columns=["ID Alternatif", "Alternatif", "ID Kriteria", "Kriteria", "Nilai", "Hasil"])
                    kriteria_order = df[["ID Kriteria", "Kriteria"]].drop_duplicates().sort_values("ID Kriteria")
                    df_pivot = df.pivot(index="Alternatif", columns=["Kriteria"], values="Nilai").reset_index()
                    df_hasil = df[["Alternatif", "Hasil"]].drop_duplicates()
                    df_pivot = df_pivot.merge(df_hasil, on="Alternatif")
                    df_pivot["Ranking"] = df_pivot["Hasil"].rank(ascending=False, method="dense").astype(int)
                    kolom_order = ["Ranking", "Alternatif"] + list(kriteria_order["Kriteria"]) + ["Hasil"]
                    df_pivot = df_pivot[kolom_order]
                    df_pivot = df_pivot.sort_values(by="Ranking", ascending=True)
                    df_pivot = df_pivot.reset_index(drop=True)

                    st.dataframe(data=df_pivot, hide_index=True, use_container_width=True)

                    kriteria_tersimpan = db.ambil_kriteria(prediksi_id)
                    st.write("#### Bobot Kriteria")
                    
                    kriteria_df = pd.DataFrame(kriteria_tersimpan, columns=["ID", "ID Prediksi", "Kriteria", "Tipe", "Bobot"])
                    kriteria_df = kriteria_df[["Kriteria", "Bobot", "Tipe"]].map(lambda x: "{:.2f}".format(x) if isinstance(x, (int, float)) else x)
                    
                    st.dataframe(data=kriteria_df, hide_index=True, use_container_width=True)
                    tanggal = pd.to_datetime(timestamp).strftime("%d %B %Y")
                    st.text(f"Diproses pada: {tanggal}")
                    st.markdown("---")
    
    if not prediksi_tersimpan:
        st.warning("Belum ada prediksi yang tersimpan.")

