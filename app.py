import streamlit as st
import numpy as np
from db_sql import Database
from models import hitung_saw, hitung_wp, hitung_topsis

# Debugging Mode
import traceback

db = Database()

st.set_page_config(page_title="DSS Framework", layout="centered")
st.title("Sistem Pendukung Keputusan - SAW, WP, TOPSIS")

# Sidebar Navigasi dengan Tampilan yang Ditingkatkan
st.sidebar.markdown("### DSS Framework")
st.sidebar.markdown("### Menu Navigasi")
menu = st.sidebar.radio("Pilih Halaman", ["🏠 Input Data", "📜 Riwayat Prediksi"])
st.sidebar.markdown("---")
st.sidebar.markdown("**Informasi Aplikasi**")
st.sidebar.text("Versi: 1.0")
st.sidebar.text("Dikembangkan oleh: Tim 2 DSS MMI24")

if menu == "🏠 Input Data":
    st.subheader("Masukkan Data Prediksi")
    nama_prediksi = st.text_input("Nama Prediksi", "")
    metode = st.selectbox("Pilih Metode", ["SAW", "WP", "TOPSIS"])
    jumlah_kriteria = 1
    jumlah_alternatif = 1
    input_jumlah_kriteria = st.number_input("Jumlah Kriteria", min_value=1, step=1, value=3)
    input_jumlah_alternatif = st.number_input("Jumlah Alternatif", min_value=1, step=1, value=3)
    update_button = st.button("Perbarui")
    
    if update_button:
        if not nama_prediksi.strip():
            st.error("Nama prediksi harus diisi.")
        else:
            jumlah_kriteria = input_jumlah_kriteria
            jumlah_alternatif = input_jumlah_alternatif

    # Menggunakan Tabs untuk Input Kriteria dan Alternatif
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
    
    with tab_alternatif:
        st.subheader("Alternatif")
        alternatif_data = []
        matrix_data = []
        for i in range(jumlah_alternatif):
            nama = st.text_input(f"Alternatif {i+1}", key=f"alt_{i}")
            nilai = [st.number_input(f"{nama} - {kriteria_data[j][0]}", min_value=0.0, key=f"nilai_{i}_{j}") for j in range(jumlah_kriteria)]
            alternatif_data.append(nama)
            matrix_data.append(nilai)
    
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
                prediksi_id = db.simpan_prediksi(nama_prediksi, metode)
                kriteria_ids = [db.simpan_kriteria(prediksi_id, k[0], k[1], k[2]) for k in kriteria_data]
                alternatif_ids = [db.simpan_alternatif(prediksi_id, a) for a in alternatif_data]
                
                matrix_np = np.array(matrix_data)
                bobot_np = np.array([k[2] for k in kriteria_data])
                tipe_kriteria = [k[1] for k in kriteria_data]
                
                hasil = None
                if metode == "SAW":
                    hasil = hitung_saw(matrix_np, bobot_np, tipe_kriteria)
                elif metode == "WP":
                    hasil = hitung_wp(matrix_np, bobot_np, tipe_kriteria)
                elif metode == "TOPSIS":
                    hasil = hitung_topsis(matrix_np, bobot_np, tipe_kriteria)
                
                if hasil is not None:
                    hasil_sorted = sorted(zip(alternatif_data, hasil), key=lambda x: x[1], reverse=True)
                    st.success("Prediksi berhasil dihitung!")
                    st.table({"Alternatif": [h[0] for h in hasil_sorted], "Skor": [h[1] for h in hasil_sorted]})
                    
                    for alt, skor in hasil_sorted:
                        db.simpan_hasil(prediksi_id, alt, skor)
                else:
                    st.error("Terjadi kesalahan saat menghitung hasil.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
                st.text(traceback.format_exc())

elif menu == "📜 Riwayat Prediksi":
    st.subheader("Riwayat Prediksi")
    search_query = st.text_input("Cari Prediksi Berdasarkan Nama")
    prediksi_tersimpan = db.ambil_prediksi()
    
    for prediksi in prediksi_tersimpan:
        prediksi_id, nama_prediksi, metode = prediksi
        if search_query.lower() in nama_prediksi.lower():
            st.write(f"### Prediksi: {nama_prediksi}")
            st.write(f"Metode: {metode}")
            
            hasil_tersimpan = db.ambil_hasil(prediksi_id)
            if hasil_tersimpan:
                st.write("#### Hasil Perhitungan")
                st.table({"Alternatif": [h[2] for h in hasil_tersimpan], "Skor": [h[3] for h in hasil_tersimpan]})
            
            kriteria_tersimpan = db.ambil_kriteria(prediksi_id)
            st.write("#### Kriteria")
            for k in kriteria_tersimpan:
                st.write(f"{k[2]} ({k[3]}) - Bobot: {k[4]}")
            
            alternatif_tersimpan = db.ambil_alternatif(prediksi_id)
            st.write("#### Alternatif")
            for a in alternatif_tersimpan:
                st.write(a[2])
    
    if not prediksi_tersimpan:
        st.warning("Belum ada prediksi yang tersimpan.")

