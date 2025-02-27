import streamlit as st
import numpy as np
import pandas as pd
from database import Database
from methods import hitung_saw, hitung_wp, hitung_topsis, normalisasi_bobot_kriteria, simpan_ke_database

db = Database(status=True)

st.set_page_config(page_title="DSS Framework", layout="centered")
st.title("Sistem Pendukung Pembuatan Keputusan - SAW, WP, TOPSIS")

st.sidebar.markdown("### DSS Framework")
st.sidebar.markdown("### Menu Navigasi")
menu = st.sidebar.radio("Pilih Halaman", ["🏠 Input Data", "📜 Riwayat"])
st.sidebar.markdown("---")
st.sidebar.text("Dikembangkan oleh:")
st.sidebar.text("Aziz Solihin, Firda Ayu Safitri, Kadek Gunamulya Sudarma Yasa")
st.sidebar.text("MMI24 UGM")

if menu == "🏠 Input Data":
    with st.form(key=f"form_dss"):
        judul_topik = st.text_input("Judul Topik", "", placeholder="Harus diisi")
        metode = st.selectbox("Pilih Metode", ["SAW", "WP", "TOPSIS"])
        colkrit, colalt = st.columns(2)
        with colkrit:
            jumlah_kriteria = st.number_input("Jumlah Kriteria", min_value=1, step=1, value=3)
        with colalt:
            jumlah_alternatif = st.number_input("Jumlah Alternatif", min_value=1, step=1, value=3)
        if st.form_submit_button("Konfirmasi"):
            if not judul_topik.strip():
                st.error("Judul topik harus diisi.")

    tab_kriteria, tab_subkriteria, tab_alternatif = st.tabs(["**Kriteria**", "**Subkriteria**", "**Alternatif**"])

    # INPUT KRITERIA
    with tab_kriteria:
        st.subheader("INPUT DATA KRITERIA")
        data_kriteria = []
        with st.form(key=f"kriteria_form"):
            for i in range(jumlah_kriteria):
                col1, col2 = st.columns(2)
                with col1:
                    nama = st.text_input(f"Nama Kriteria {i+1}", key=f"kriteria_{i}")
                    tipe = st.radio(f"Tipe Kriteria {i+1}", ["benefit", "cost"], key=f"tipe_krit_{i}")
                with col2:
                    bobot = st.number_input(f"Bobot Kriteria {i+1}", 0.0, step=0.05, key=f"bobot_krit_{i}")
                    jumlah_subkriteria = st.number_input(f"Jumlah Subkriteria", min_value=0, step=1, value=0, key=f"jumlah_sub_{i}")
                data_kriteria.append({
                    "Nama": nama, 
                    "Bobot": bobot, 
                    "Tipe": tipe, 
                    "Subkriteria": jumlah_subkriteria 
                })
                st.markdown("---")
            if st.form_submit_button("Konfirmasi"):
                if not all(k['Nama'].strip() for k in data_kriteria):
                    st.error("Semua nama kriteria harus diisi.")

    # INPUT SUBKRITERIA
    with tab_subkriteria:
        data_subkrit = {}
        if all(k["Subkriteria"] == 0 for k in data_kriteria):
            st.info("Silahkan isi Jumlah Subkriteria pada menu **Kriteria**. Jika tidak ada, lewati menu ini.")
        else:
            st.subheader("INPUT DATA SUBKRITERIA")
            with st.form(key=f"subkriteria_form"):
                for k in data_kriteria: 
                    if k["Subkriteria"] > 0:
                        subkriteria_list = []
                        st.subheader(k['Nama'])
                        for i in range(k["Subkriteria"]):
                            col1, col2 = st.columns(2)
                            with col1:
                                nama = st.text_input(f"Nama Subkriteria {i+1}", key=f"subkriteria_{k['Nama']}{i}")
                            with col2:
                                bobot = st.number_input(f"Bobot Subkriteria", 0.0, step=0.05, key=f"bobot_subkrit_{k['Nama']}{i}")
                                tipe = st.radio(f"Tipe Subkriteria", ["benefit", "cost"], key=f"tipe_subkrit_{k['Nama']}{i}")
                            subkriteria_list.append({
                                "Nama": nama,
                                "Bobot": bobot,
                                "Tipe": tipe
                            })
                        data_subkrit[k['Nama']] = subkriteria_list
                        st.markdown("---")
                if st.form_submit_button("Konfirmasi"):
                    if not all(s['Nama'].strip() for s in subkriteria_list):
                        st.error("Semua nama subkriteria harus diisi.")

    # INPUT ALTERNATIF
    with tab_alternatif:
        st.subheader("INPUT DATA ALTERNATIF")
        data_alternatif = []
        data_matrix = []
        data_nilai = []
        data_nilai = np.full((jumlah_alternatif, jumlah_kriteria), -1, float)
        data_subnilai = []
        with st.form(f"alternatif_form"):
            for i in range(jumlah_alternatif):
                nama = st.text_input(f"Nama Alternatif {i+1}", key=f"alt_{i}")
                matrix_list = []
                subnilai_list = []
                for j, k in enumerate(data_kriteria):
                    if k["Subkriteria"] > 0 and k['Nama'] in data_subkrit:
                        data = data_subkrit[k['Nama']]
                        for n, d in enumerate(data):
                            nilai = st.number_input(f"{k['Nama']} {d['Nama']} ({d['Tipe']})", min_value=0.0, key=f"nilai_{i}{j}{n}")
                            matrix_list.append(nilai)
                            subnilai_list.append(nilai) # untuk database
                    else:
                        nilai = st.number_input(f"{k['Nama']} ({k['Tipe']})", min_value=0.0, key=f"nilai_{i}{j}")
                        matrix_list.append(nilai)
                        data_nilai[i][j] = nilai # untuk database
                data_alternatif.append({
                    "Nama": nama,
                    "Nilai": matrix_list
                })
                data_matrix.append(matrix_list)
                data_subnilai.append(subnilai_list) # untuk database
                st.markdown("---")
            if st.form_submit_button("Konfirmasi"):
                if not all(data_alternatif) or not all(a['Nama'].strip() for a in data_alternatif):
                    st.error("Semua nama alternatif harus diisi.")
                elif not all(data_matrix):
                    st.error("Semua nilai alternatif harus diisi.")
    
    submit = st.button(f"Validasi & Hitung dengan {metode}", use_container_width=True, type="primary")
    if submit:  
        if not judul_topik.strip():
            st.error("Judul topik harus diisi.")
        elif not all(k['Nama'].strip() for k in data_kriteria):
            st.error("Semua nama kriteria harus diisi.")
        elif not all(data_alternatif) or not all(a['Nama'].strip() for a in data_alternatif):
            st.error("Semua nama alternatif harus diisi.")  
        elif not all(data_matrix):
            st.error("Semua nilai alternatif harus diisi.")
        else:
            # data_kriteria
            # data_subkrit
            # data_alternatif
            # data_matrix
            # data_nilai
            # data_subnilai

            with st.spinner("Sedang memproses..."):
                norm_data_krit = normalisasi_bobot_kriteria(data_kriteria, data_subkrit)
                krit_nama = [k['Nama'] for k in norm_data_krit]
                alt_nama = [a['Nama'] for a in data_alternatif]

                hasil = None
                if metode == "SAW":
                    hasil = hitung_saw(data_matrix, norm_data_krit)
                elif metode == "WP":
                    hasil = hitung_wp(data_matrix, norm_data_krit)
                elif metode == "TOPSIS":
                    hasil = hitung_topsis(data_matrix, norm_data_krit)

                rd_hasil = np.round(hasil, 3)
                if hasil is not None:
                    simpan_ke_database(db, judul_topik, metode, data_kriteria, data_subkrit, data_alternatif, data_nilai, data_subnilai, rd_hasil)
                    st.success("Proses selesai.")
                
                df_hasil = pd.DataFrame({
                    "Alternatif" : alt_nama,
                    "Hasil": rd_hasil
                })

                df_hasil["Rank"] = df_hasil["Hasil"].rank(method="dense", ascending=False).astype(int)
                df_hasil = df_hasil.sort_values(by="Rank").set_index("Rank")
                st.dataframe(df_hasil, use_container_width=True)
                
                st.subheader("Riwayat Input Data")
                df_krit = pd.DataFrame(norm_data_krit)
                df_krit = df_krit.round({"Bobot": 3})
                df_krit = df_krit.T
                st.write("Normalisasi Bobot Kriteria")
                st.dataframe(df_krit, use_container_width=True)
                df_tabel = pd.DataFrame(data_matrix, index=alt_nama, columns=krit_nama)
                st.write("Nilai Parameter")
                st.dataframe(df_tabel, use_container_width=True)

elif menu == "📜 Riwayat":
    st.subheader("Riwayat Proses")
    with st.form(key="search_form", border=False):
        search_query = st.text_input("", placeholder="Cari berdasarkan topik atau metode...")
        st.form_submit_button("Cari", use_container_width=True)
    if db is None:
        st.error("Koneksi ke database gagal.")
    else:
        data_topik = db.ambil_topik()
        if data_topik:
            for topik in data_topik:
                topik_id, judul, metode, timestamp = topik
                if search_query.lower() in judul.lower() or search_query.lower() in metode.lower():
                    with st.expander(f"{judul} - {metode}", expanded=False):
                        st.write(f"### Topik: {judul}")
                        st.write(f"Metode: {metode}")
                        with st.spinner("Sedang memuat..."):
                            df = db.ambil_pivot_data(topik_id)
                            st.dataframe(df, use_container_width=True)
                            st.write("Tabel Kriteria")
                            df_kriteria = db.ambil_pivot_kriteria(topik_id)
                            st.dataframe(df_kriteria, use_container_width=True, hide_index=True)
        else:
            st.info("Data tidak ditemukan")
