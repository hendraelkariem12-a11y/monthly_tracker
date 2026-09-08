import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# CONFIG & KONEKSI GOOGLE SHEETS
# ---------------------------------------------------------
st.set_page_config(page_title="Monthly Progress Tracker", layout="wide", page_icon="📈")

@st.cache_resource
def get_gspread_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

try:
    client = get_gspread_client()
    sheet_url = "https://docs.google.com/spreadsheets/d/17-zwnUwDzk9jxx1_jnFyqJ2SSC1xHT5nZ6dZdHgfGvA/edit"
    spreadsheet = client.open_by_url(sheet_url)
    
    ws_log = spreadsheet.worksheet("Log_Mingguan")
    
    try:
        ws_custom = spreadsheet.worksheet("Category_Custom")
    except:
        ws_custom = spreadsheet.worksheet("Kategori_Custom")
        
    ws_bulanan = spreadsheet.worksheet("Pencapaian_Bulanan")
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheets: {e}")
    st.info("Pastikan pengaturan Secrets st.secrets['gcp_service_account'] sudah terpasang dengan benar.")
    st.stop()

def load_data(worksheet):
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION (Definisi Variabel `menu`)
# ---------------------------------------------------------
st.sidebar.title("📌 Menu Utama")
menu = st.sidebar.radio("Pilih Halaman:", [
    "📊 Dashboard & Rekapitulasi",
    "📝 Input Progress Mingguan",
    "🎯 Input Pencapaian Bulanan",
    "⚙️ Kelola Metrik & Kategori Baru"
])

# ---------------------------------------------------------
# 1. DASHBOARD & RINGKASAN PROFIL
# ---------------------------------------------------------
if menu == "📊 Dashboard & Rekapitulasi":
    st.title("📌 Personal Progress Dashboard")
    
    default_foto_url = "https://i.ibb.co/sample-image.jpg" 
    
    with st.sidebar.expander("🖼️ Pengaturan Foto Profil"):
        foto_url = st.text_input("Link Foto ImgBB (Direct Link):", value=default_foto_url)

    df_log = load_data(ws_log)
    df_b = load_data(ws_bulanan)
    
    bulan_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    if not df_log.empty and "Bulan" in df_log.columns:
        existing_months = [b for b in df_log["Bulan"].unique() if b in bulan_list]
        if existing_months:
            bulan_list = existing_months

    bulan_selected = st.selectbox("🗓️ Pilih Bulan Tinjauan:", bulan_list)

    st.divider()

    col_foto, col_info = st.columns([1, 3], gap="medium")
    
    with col_foto:
        if foto_url:
            st.image(foto_url, caption="Dede Suhendra", use_container_width=True)
        else:
            st.info("Tempel link foto ImgBB di sidebar.")

    with col_info:
        st.subheader(f"👋 Laporan Perkembangan Diri — {bulan_selected}")
        st.write(
            f"Selamat datang di ringkasan pencapaian personal bulan **{bulan_selected}**. "
            "Berikut adalah akumulasi komitmen harian dan mingguan dalam aspek "
            "**Pengetahuan, Agama, Kesehatan, dan Keuangan**."
        )
        
        evaluasi_text = "Belum ada catatan evaluasi untuk bulan ini."
        if not df_b.empty and "Bulan" in df_b.columns:
            df_b_filter = df_b[df_b["Bulan"] == bulan_selected]
            if not df_b_filter.empty:
                evaluasi_text = df_b_filter.iloc[-1].get('Evaluasi Umum & Catatan', evaluasi_text)

        st.info(f"💡 **Catatan / Evaluasi Bulan Ini:**\n\n_{evaluasi_text}_")

    st.divider()

    st.markdown("### 🎯 Angka Kunci Pencapaian Bulan Ini")
    
    if not df_log.empty:
        df_filtered = df_log[df_log["Bulan"] == bulan_selected]
        
        if not df_filtered.empty:
            df_agg = df_filtered.groupby(["Kategori", "Metrik / Nama Kegiatan"])["Nilai"].sum().reset_index()
            
            m1, m2, m3, m4 = st.columns(4)
            
            b_inggris = df_agg[df_agg["Metrik / Nama Kegiatan"] == "Belajar B. Inggris"]["Nilai"].sum() if not df_agg.empty else 0
            quran_juz = df_agg[df_agg["Metrik / Nama Kegiatan"] == "Baca Qur'an"]["Nilai"].sum() if not df_agg.empty else 0
            jogging_min = df_agg[df_agg["Metrik / Nama Kegiatan"] == "Jogging"]["Nilai"].sum() if not df_agg.empty else 0
            
            pemasukan = df_agg[df_agg["Metrik / Nama Kegiatan"] == "Pemasukan"]["Nilai"].sum() if not df_agg.empty else 0
            pengeluaran = df_agg[df_agg["Metrik / Nama Kegiatan"] == "Pengeluaran"]["Nilai"].sum() if not df_agg.empty else 0
            tabungan = pemasukan - pengeluaran

            m1.metric("📚 B. Inggris", f"{b_inggris} Menit")
            m2.metric("📖 Baca Qur'an", f"{quran_juz} Juz")
            m3.metric("🏃 Jogging", f"{jogging_min} Menit")
            m4.metric("💰 Tabungan Bersih", f"Rp {tabungan:,.0f}")

            st.divider()

            st.markdown("### 📋 Ringkasan Detail Per Kategori")
            
            tab_pengetahuan, tab_agama, tab_kesehatan, tab_keuangan = st.tabs([
                "🧠 Pengetahuan", "🕌 Agama", "🏃 Kesehatan", "💵 Keuangan"
            ])

            with tab_pengetahuan:
                st.markdown("#### Progress Pengetahuan & Pengembangan Diri")
                df_p = df_filtered[df_filtered["Kategori"] == "Pengetahuan"]
                st.dataframe(df_p[["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)

            with tab_agama:
                st.markdown("#### Progress Amalan & Ibadah")
                df_a = df_filtered[df_filtered["Kategori"] == "Agama"]
                st.dataframe(df_a[["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)

            with tab_kesehatan:
                st.markdown("#### Progress Latihan Fisik & Olahraga")
                df_k = df_filtered[df_filtered["Kategori"] == "Kesehatan"]
                st.dataframe(df_k[["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)

            with tab_keuangan:
                st.markdown("#### Ringkasan Arus Kas")
                df_f = df_filtered[df_filtered["Kategori"] == "Keuangan"]
                st.dataframe(df_f[["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)

            st.divider()
            st.markdown("### 📈 Grafik Perkembangan Mingguan (Minggu 1–4)")
            kat_grafik = st.selectbox("Pilih Kategori untuk Dilihat Grafik Trennya:", df_filtered["Kategori"].unique())
            df_grafik = df_filtered[df_filtered["Kategori"] == kat_grafik]

            fig = px.bar(
                df_grafik, 
                x="Minggu", 
                y="Nilai", 
                color="Metrik / Nama Kegiatan", 
                barmode="group",
                text_auto=True,
                title=f"Grafik Pencapaian {kat_grafik} per Minggu"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"Belum ada data log mingguan untuk bulan {bulan_selected}.")
    else:
        st.info("Belum ada data log mingguan yang diinput.")

# ---------------------------------------------------------
# 2. INPUT PROGRESS MINGGUAN
# ---------------------------------------------------------
elif menu == "📝 Input Progress Mingguan":
    st.title("📝 Form Input Progress Mingguan")
    st.write("Catat perkembangan mingguan kamu untuk pengetahuan, agama, kesehatan, dan keuangan.")

    df_custom = load_data(ws_custom)
    
    if df_custom.empty:
        default_metrics = [
            {"Kategori": "Pengetahuan", "Nama Metrik": "Artikel Dibaca", "Satuan": "Artikel"},
            {"Kategori": "Pengetahuan", "Nama Metrik": "Belajar B. Inggris", "Satuan": "Menit"},
            {"Kategori": "Pengetahuan", "Nama Metrik": "Belajar B. Arab", "Satuan": "Menit"},
            {"Kategori": "Pengetahuan", "Nama Metrik": "Buku Fisik Dibaca", "Satuan": "Buku"},
            {"Kategori": "Pengetahuan", "Nama Metrik": "E-Book Dibaca", "Satuan": "Buku"},
            {"Kategori": "Pengetahuan", "Nama Metrik": "Catatan / Buku Dibuat", "Satuan": "Buat"},
            {"Kategori": "Pengetahuan", "Nama Metrik": "Hafalan Al-Qur'an", "Satuan": "Surah/Juz"},
            {"Kategori": "Agama", "Nama Metrik": "Salat Dhuha", "Satuan": "Kali"},
            {"Kategori": "Agama", "Nama Metrik": "Salat Tahajud", "Satuan": "Kali"},
            {"Kategori": "Agama", "Nama Metrik": "Baca Qur'an", "Satuan": "Juz"},
            {"Kategori": "Agama", "Nama Metrik": "Zikir Pagi Petang", "Satuan": "Kali"},
            {"Kategori": "Kesehatan", "Nama Metrik": "Jogging", "Satuan": "Menit"},
            {"Kategori": "Kesehatan", "Nama Metrik": "Push Up", "Satuan": "Reps"},
            {"Kategori": "Kesehatan", "Nama Metrik": "Squat Jump", "Satuan": "Reps"},
            {"Kategori": "Keuangan", "Nama Metrik": "Pemasukan", "Satuan": "Rp"},
            {"Kategori": "Keuangan", "Nama Metrik": "Pengeluaran", "Satuan": "Rp"}
        ]
        ws_custom.append_rows([list(d.values()) for d in default_metrics])
        df_custom = load_data(ws_custom)

    with st.form("form_mingguan"):
        col1, col2 = st.columns(2)
        with col1:
            bulan = st.selectbox("Pilih Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                                                "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        with col2:
            minggu = st.selectbox("Pilih Minggu", ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"])
        
        st.divider()
        
        input_data = []
        kategori_list = df_custom["Kategori"].unique() if "Kategori" in df_custom.columns else []

        for kat in kategori_list:
            st.subheader(f"🔹 Kategori: {kat}")
            metrics = df_custom[df_custom["Kategori"] == kat]
            
            for _, row in metrics.iterrows():
                metrik_nama = row["Nama Metrik"]
                satuan = row["Satuan"]
                
                c_val, c_note = st.columns([2, 3])
                with c_val:
                    if satuan == "Rp":
                        nilai = st.number_input(f"{metrik_nama} ({satuan})", min_value=0, step=50000, key=f"{bulan}_{minggu}_{metrik_nama}")
                    else:
                        nilai = st.number_input(f"{metrik_nama} ({satuan})", min_value=0, step=1, key=f"{bulan}_{minggu}_{metrik_nama}")
                with c_note:
                    catatan = st.text_input(f"Catatan untuk {metrik_nama}", key=f"note_{bulan}_{minggu}_{metrik_nama}")
                
                input_data.append([bulan, minggu, kat, metrik_nama, nilai, satuan, catatan])
            st.markdown("---")

        submit_btn = st.form_submit_button("💾 Simpan Data Mingguan")

    if submit_btn:
        with st.spinner("Menyimpan data ke Google Sheets..."):
            ws_log.append_rows(input_data)
            st.success(f"✅ Data perkembangan untuk {bulan} ({minggu}) berhasil disimpan!")

# ---------------------------------------------------------
# 3. INPUT PENCAPAIAN BULANAN
# ---------------------------------------------------------
elif menu == "🎯 Input Pencapaian Bulanan":
    st.title("🎯 Pencapaian Umum 1 Bulan")
    st.write("Tuliskan evaluasi & pencapaian umum kualitatif di akhir bulan.")

    with st.form("form_bulanan"):
        bulan_eval = st.selectbox("Pilih Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                                                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        
        pengetahuan_eval = st.text_area("Pencapaian Pengetahuan", placeholder="Misal: Berhasil menamatkan 2 buku & konsisten latihan B. Inggris...")
        agama_eval = st.text_area("Pencapaian Agama", placeholder="Misal: Alhamdulillah salat tahajud dan dhuha rutin, hafalan bertambah...")
        kesehatan_eval = st.text_area("Pencapaian Kesehatan", placeholder="Misal: Fisik terasa lebih segar, jogging rutin tiap akhir pekan...")
        keuangan_eval = st.text_area("Pencapaian Keuangan", placeholder="Misal: Cashflow positif, pengeluaran terkelola dengan baik...")
        evaluasi_umum = st.text_area("Evaluasi Umum & Catatan Diri", placeholder="Poin-poin evaluasi yang perlu ditingkatkan bulan depan...")

        submit_bulanan = st.form_submit_button("💾 Simpan Evaluasi Bulanan")

    if submit_bulanan:
        with st.spinner("Menyimpan ke Google Sheets..."):
            row_bulanan = [bulan_eval, pengetahuan_eval, agama_eval, kesehatan_eval, keuangan_eval, evaluasi_umum]
            ws_bulanan.append_row(row_bulanan)
            st.success(f"✅ Evaluasi bulanan untuk {bulan_eval} berhasil disimpan!")

# ---------------------------------------------------------
# 4. KELOLA METRIK & KATEGORI BARU
# ---------------------------------------------------------
elif menu == "⚙️ Kelola Metrik & Kategori Baru":
    st.title("⚙️ Tambah Metrik / Kategori Baru")
    st.write("Gunakan menu ini jika di kemudian hari ingin menambah parameter atau kategori tracker baru.")

    df_custom = load_data(ws_custom)
    
    with st.form("form_tambah_metrik"):
        st.subheader("Form Tambah Parameter Baru")
        kat_baru = st.text_input("Nama Kategori", placeholder="Misal: Side Project, Hobi, Dll.")
        metrik_baru = st.text_input("Nama Metrik / Kegiatan", placeholder="Misal: Coding Jam, Baca Artikel Tech...")
        satuan_baru = st.text_input("Satuan", placeholder="Misal: Jam, Menit, Kali, Rp...")
        
        submit_custom = st.form_submit_button("➕ Tambahkan Metrik Baru")

    if submit_custom:
        if kat_baru and metrik_baru and satuan_baru:
            ws_custom.append_row([kat_baru, metrik_baru, satuan_baru])
            st.success(f"✅ Metrik '{metrik_baru}' berhasil ditambahkan ke kategori '{kat_baru}'!")
            st.rerun()
        else:
            st.warning("Mohon isi seluruh field form di atas.")

    st.divider()
    st.subheader("Daftar Metrik & Kategori Saat Ini")
    st.dataframe(df_custom, use_container_width=True)
