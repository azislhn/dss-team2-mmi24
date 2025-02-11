import streamlit as st
import numpy as np
from db_sql import Database
from models import hitung_saw, hitung_wp, hitung_topsis

db = Database()

st.set_page_config(page_title="DSS Framework", layout="centered")
st.title("Sistem Pendukung Keputusan - SAW, WP, TOPSIS")

# Sidebar Navigasi dengan Tampilan yang Ditingkatkan
st.sidebar.markdown("## DSS Framework")
st.sidebar.markdown("### Menu Navigasi")
menu = st.sidebar.radio("Pilih Halaman", ["🏠 Input Data", "📜 Riwayat Prediksi"])
st.sidebar.markdown("---")
st.sidebar.markdown("**Informasi Aplikasi**")
st.sidebar.text("Versi: 1.0")
st.sidebar.text("Dikembangkan oleh: Tim 2 DSS MMI24")

if menu == "🏠 Input Data":
    with st.form("form_prediksi"):
        st.subheader("Masukkan Data Prediksi")
        nama_prediksi = st.text_input("Nama Prediksi", "")
        metode = st.selectbox("Pilih Metode", ["SAW", "WP", "TOPSIS"])
        jumlah_kriteria = 1
        jumlah_alternatif = 1
        input_jumlah_kriteria = st.number_input("Jumlah Kriteria", min_value=1, step=1, value=1)
        input_jumlah_alternatif = st.number_input("Jumlah Alternatif", min_value=1, step=1, value=1)

        update_setting = st.form_submit_button("Perbarui")
        if update_setting:
            jumlah_kriteria = input_jumlah_kriteria
            jumlah_alternatif = input_jumlah_alternatif

        # Tabs untuk Kriteria dan Alternatif
        tab1, tab2 = st.tabs(["Kriteria", "Alternatif"])

        with tab1:
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

        with tab2:
            st.subheader("Alternatif")
            alternatif_data = []
            matrix_data = []
            for i in range(jumlah_alternatif):
                nama = st.text_input(f"Alternatif {i+1}", key=f"alt_{i}")
                nilai = [st.number_input(f"{nama} - {kriteria_data[j][0]}", min_value=0.0, key=f"nilai_{i}_{j}") for j in range(jumlah_kriteria)]
                alternatif_data.append(nama)
                matrix_data.append(nilai)
                st.markdown("---")

        submit = st.form_submit_button(f"Simpan & Hitung dengan {metode}")

    if submit:
        if (not nama_prediksi or not metode or
            not all(k[0] for k in kriteria_data) or # Memastikan semua nama kriteria diisi
            not all(alternatif_data) or  # Memastikan semua alternatif diisi
            not all(all(val is not None for val in row) for row in matrix_data)):  # Memastikan semua nilai alternatif diisi
            st.error("Semua data harus diisi sebelum melakukan prediksi.")
        else:
            prediksi_id = db.simpan_prediksi(nama_prediksi, metode)
            kriteria_ids = [db.simpan_kriteria(prediksi_id, k[0], k[1], k[2]) for k in kriteria_data]
            alternatif_ids = [db.simpan_alternatif(prediksi_id, a) for a in alternatif_data]

            matrix_np = np.array(matrix_data)
            tipe_kriteria = [k[1] for k in kriteria_data]
            bobot_np = np.array([k[2] for k in kriteria_data])

            if metode == "SAW":
                hasil = hitung_saw(matrix_np, bobot_np, tipe_kriteria)
            elif metode == "WP":
                hasil = hitung_wp(matrix_np, bobot_np, tipe_kriteria)
            elif metode == "TOPSIS":
                hasil = hitung_topsis(matrix_np, bobot_np, tipe_kriteria)

            hasil_sorted = sorted(zip(alternatif_data, hasil), key=lambda x: x[1], reverse=True)

            st.success("Prediksi berhasil dihitung!")
            st.table({"Alternatif": [h[0] for h in hasil_sorted], "Skor": [h[1] for h in hasil_sorted]})

            for alt, skor in hasil_sorted:
                db.simpan_hasil(prediksi_id, alt, skor)

# elif menu == "📜 Riwayat Prediksi":
#     st.subheader("Riwayat Prediksi")
#     if db.is_connected():
#         prediksi_tersimpan = db.db.collection("prediksi").stream()
#         for doc in prediksi_tersimpan:
#             st.write(f"### Prediksi: {doc.to_dict()['nama_prediksi']}")
#             st.write(f"Metode: {doc.to_dict()['metode']}")
#     else:
#         st.warning("Tidak terhubung ke database.")
    
elif menu == "📜 Riwayat Prediksi":
    st.subheader("Riwayat Prediksi")
    prediksi_tersimpan = db.ambil_prediksi()
    
    for prediksi in prediksi_tersimpan:
        prediksi_id, nama_prediksi, metode = prediksi
        st.write(f"### Prediksi: {nama_prediksi}")
        st.write(f"Metode: {metode}")
        
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

