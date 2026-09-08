import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# CONFIG & KONEKSI GOOGLE SHEETS
# ---------------------------------------------------------
st.set_page_config(page_title="Monthly Progress & Finance Journal", layout="centered", page_icon="📈")

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
    st.info("Pastikan Secrets st.secrets['gcp_service_account'] terpasang dengan benar.")
    st.stop()

def load_data(worksheet):
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.title("📌 Menu Utama")
menu = st.sidebar.radio("Pilih Halaman:", [
    "📖 Timeline Progress Bulanan",
    "📝 Input Progress Mingguan",
    "🎯 Input Evaluasi & Foto Bulanan",
    "⚙️ Kelola Metrik & Kategori Baru"
])

# ---------------------------------------------------------
# 1. TIMELINE PROGRESS BULANAN (FOTO PER BULAN + NERACA KEUANGAN)
# ---------------------------------------------------------
if menu == "📖 Timeline Progress Bulanan":
    st.title("📖 Jurnal & Timeline Perkembangan Diri")
    st.write("Merekam perjalanan fisik, pengetahuan, ibadah, kesehatan, dan kondisi keuangan dari bulan ke bulan.")

    df_log = load_data(ws_log)
    df_b = load_data(ws_bulanan)

    bulan_list = []
    if not df_log.empty and "Bulan" in df_log.columns:
        bulan_list = list(df_log["Bulan"].unique())

    if not df_b.empty and "Bulan" in df_b.columns:
        for b in df_b["Bulan"].unique():
            if b not in bulan_list and b != "":
                bulan_list.append(b)

    if not bulan_list:
        st.info("Belum ada data yang diinput. Mulai dari menu 'Input Progress Mingguan' atau 'Input Evaluasi & Foto Bulanan'.")
    else:
        # Tampilkan riwayat dari bulan terbaru ke terlama (Scroll ke bawah)
        for bulan_item in reversed(bulan_list):
            st.markdown(f"# 📅 Bulan {bulan_item}")
            
            # Ambil data evaluasi & foto bulanan
            foto_bulan = "https://via.placeholder.com/300x400?text=Foto+Belum+Diupload"
            evaluasi_text = "Belum ada catatan evaluasi untuk bulan ini."
            
            if not df_b.empty and "Bulan" in df_b.columns:
                df_b_filter = df_b[df_b["Bulan"] == bulan_item]
                if not df_b_filter.empty:
                    row_b = df_b_filter.iloc[-1]
                    evaluasi_text = row_b.get('Evaluasi Umum & Catatan', evaluasi_text)
                    if row_b.get('Foto_URL') and str(row_b.get('Foto_URL')).strip() != "":
                        foto_bulan = str(row_b.get('Foto_URL')).strip()

            # Tampilan Profil Per Bulan
            col_img, col_info = st.columns([1, 2], gap="medium")
            with col_img:
                st.image(foto_bulan, caption=f"Foto Fisik — {bulan_item}", use_container_width=True)
            with col_info:
                st.subheader("Dede Suhendra")
                st.caption(f"Laporan Perkembangan Diri — {bulan_item}")
                st.info(f"💡 **Evaluasi & Catatan Diri:**\n\n_{evaluasi_text}_")

            # Tampilkan Ringkasan Keuangan Real-time (Balance Sheet)
            if not df_log.empty and "Bulan" in df_log.columns:
                df_filtered = df_log[df_log["Bulan"] == bulan_item]
                
                if not df_filtered.empty:
                    st.markdown("### 💰 Perkembangan Keuangan Bulan Ini")
                    df_keu = df_filtered[df_filtered["Kategori"] == "Keuangan"]
                    
                    if not df_keu.empty:
                        # Ambil nilai terakhir (atau total)
                        s_bank = df_keu[df_keu["Metrik / Nama Kegiatan"].str.contains("Bank", case=False, na=False)]["Nilai"].sum()
                        s_dana = df_keu[df_keu["Metrik / Nama Kegiatan"].str.contains("DANA", case=False, na=False)]["Nilai"].sum()
                        s_cash = df_keu[df_keu["Metrik / Nama Kegiatan"].str.contains("Cash", case=False, na=False)]["Nilai"].sum()
                        s_piutang = df_keu[df_keu["Metrik / Nama Kegiatan"].str.contains("Piutang", case=False, na=False)]["Nilai"].sum()
                        s_utang = df_keu[df_keu["Metrik / Nama Kegiatan"].str.contains("Utang Saya", case=False, na=False)]["Nilai"].sum()

                        total_aset = s_bank + s_dana + s_cash + s_piutang
                        net_worth = total_aset - s_utang

                        f1, f2, f3 = st.columns(3)
                        f1.metric("💳 Bank", f"Rp {s_bank:,.0f}")
                        f2.metric("📱 DANA", f"Rp {s_dana:,.0f}")
                        f3.metric("💵 Cash", f"Rp {s_cash:,.0f}")

                        f4, f5, f6 = st.columns(3)
                        f4.metric("🤝 Piutang (Diutangin)", f"Rp {s_piutang:,.0f}")
                        f5.metric("⚠️ Utang Saya", f"Rp {s_utang:,.0f}", delta=f"-Rp {s_utang:,.0f}", delta_color="inverse")
                        f6.metric("💎 Total Kekayaan Bersih", f"Rp {net_worth:,.0f}")

                    st.markdown("---")
                    
                    # Tab Detail Kategori
                    with st.expander(f"🔍 Lihat Detail Aktivitas Mingguan ({bulan_item})"):
                        t1, t2, t3, t4 = st.tabs(["🧠 Pengetahuan", "🕌 Agama", "🏃 Kesehatan", "💵 Keuangan Detail"])
                        
                        with t1:
                            st.dataframe(df_filtered[df_filtered["Kategori"] == "Pengetahuan"][["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)
                        with t2:
                            st.dataframe(df_filtered[df_filtered["Kategori"] == "Agama"][["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)
                        with t3:
                            st.dataframe(df_filtered[df_filtered["Kategori"] == "Kesehatan"][["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)
                        with t4:
                            st.dataframe(df_filtered[df_filtered["Kategori"] == "Keuangan"][["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)

            st.markdown("---")
            st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INPUT PROGRESS MINGGUAN
# ---------------------------------------------------------
elif menu == "📝 Input Progress Mingguan":
    st.title("📝 Form Input Progress Mingguan")
    st.write("Catat perkembangan angka mingguan kamu.")

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
            {"Kategori": "Keuangan", "Nama Metrik": "Saldo Bank", "Satuan": "Rp"},
            {"Kategori": "Keuangan", "Nama Metrik": "Saldo DANA", "Satuan": "Rp"},
            {"Kategori": "Keuangan", "Nama Metrik": "Cash / Tunai", "Satuan": "Rp"},
            {"Kategori": "Keuangan", "Nama Metrik": "Piutang (Dibutuhkan Orang)", "Satuan": "Rp"},
            {"Kategori": "Keuangan", "Nama Metrik": "Utang Saya", "Satuan": "Rp"}
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
# 3. INPUT EVALUASI & FOTO BULANAN
# ---------------------------------------------------------
elif menu == "🎯 Input Evaluasi & Foto Bulanan":
    st.title("🎯 Form Evaluasi & Upload Foto Bulanan")
    st.write("Upload foto diri kamu bulan ini dan tuliskan ringkasan evaluasi bulanan.")

    with st.form("form_bulanan"):
        bulan_eval = st.selectbox("Pilih Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                                                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        
        foto_url_input = st.text_input("Link Foto ImgBB Bulan Ini (Direct Link .jpg/.png):", placeholder="https://i.ibb.co/xxxx/foto.jpg")
        
        pengetahuan_eval = st.text_area("Pencapaian Pengetahuan", placeholder="Ringkasan buku, artikel, dan bahasa yang dipelajari...")
        agama_eval = st.text_area("Pencapaian Agama", placeholder="Ringkasan ibadah, hafalan, dan amalan...")
        kesehatan_eval = st.text_area("Pencapaian Kesehatan", placeholder="Perkembangan fisik, olahraga, dan kondisi tubuh...")
        keuangan_eval = st.text_area("Pencapaian Keuangan", placeholder="Perkembangan aset, tabungan, atau pelunasan utang...")
        evaluasi_umum = st.text_area("Evaluasi Umum & Catatan Diri", placeholder="Evaluasi hal yang perlu diperbaiki bulan depan...")

        submit_bulanan = st.form_submit_button("💾 Simpan Evaluasi & Foto Bulanan")

    if submit_bulanan:
        with st.spinner("Menyimpan ke Google Sheets..."):
            row_bulanan = [bulan_eval, pengetahuan_eval, agama_eval, kesehatan_eval, keuangan_eval, evaluasi_umum, foto_url_input]
            ws_bulanan.append_row(row_bulanan)
            st.success(f"✅ Evaluasi & Foto bulanan untuk {bulan_eval} berhasil disimpan!")

# ---------------------------------------------------------
# 4. KELOLA METRIK & KATEGORI BARU
# ---------------------------------------------------------
elif menu == "⚙️ Kelola Metrik & Kategori Baru":
    st.title("⚙️ Tambah Metrik / Kategori Baru")
    st.write("Gunakan menu ini jika di kemudian hari ingin menambah parameter baru.")

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
