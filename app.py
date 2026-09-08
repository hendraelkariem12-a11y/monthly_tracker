import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# ---------------------------------------------------------
# CONFIG & PAGE SETUP
# ---------------------------------------------------------
st.set_page_config(
    page_title="Monthly Progress & Finance Journal",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ASSETS MLBB IMAGE LINKS (CLEAN TRANSPARENT PNG)
# ---------------------------------------------------------
IMG_FRAME = "https://i.ibb.co.com/Pzgqj1wD/1788849011671-removebg-preview.png"
IMG_HERO_MAIN = "https://i.ibb.co.com/SXmxTtfn/1788848932501-removebg-preview.png"
IMG_ICON_PENG = "https://i.ibb.co.com/pjSJJXgJ/1788848846642-removebg-preview.png"
IMG_ICON_AGAMA = "https://i.ibb.co.com/wrKqkpqf/1788849113579-removebg-preview.png"
IMG_ICON_KES = "https://i.ibb.co.com/zhm13rJD/1788849195681-removebg-preview.png"
IMG_ICON_KEU = "https://i.ibb.co.com/2YpL6vjZ/1788849240997-removebg-preview.png"

# ---------------------------------------------------------
# CUSTOM CSS (FRAME PRESISI & FOTO DIPERBESAR)
# ---------------------------------------------------------
custom_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700;800&family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

.stApp {{
    background: radial-gradient(circle at top right, #1e1b4b, #0f172a 60%, #020617 100%);
    color: #f8fafc;
}}

.glass-card {{
    background: rgba(15, 23, 42, 0.75) !important;
    backdrop-filter: blur(14px);
    border: 1px solid rgba(234, 179, 8, 0.25);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
}}

.gradient-header {{
    font-family: 'Rajdhani', sans-serif;
    background: linear-gradient(90deg, #38bdf8 0%, #eab308 50%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}}

.timeline-badge {{
    display: inline-block;
    padding: 6px 18px;
    border-radius: 9999px;
    background: linear-gradient(90deg, #d97706, #eab308);
    color: #020617;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 800;
    margin-bottom: 12px;
}}

/* BOX CONTAINER BINGKAI MLBB & FOTO BESAR PRESISI */
.avatar-box {{
    position: relative;
    width: 180px;
    height: 180px;
    margin: 0 auto;
}}

.user-photo {{
    width: 130px;
    height: 130px;
    border-radius: 50%;
    object-fit: cover;
    position: absolute;
    top: 25px;
    left: 25px;
    z-index: 1;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
}}

.frame-overlay {{
    width: 180px;
    height: 180px;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 2;
    pointer-events: none;
    object-fit: contain;
}}

.hero-img-display {{
    max-width: 150px;
    height: auto;
    display: block;
    margin: 0 auto;
    filter: drop-shadow(0 8px 15px rgba(0,0,0,0.5));
}}

.metric-box {{
    background: rgba(30, 41, 59, 0.6);
    border-radius: 16px;
    padding: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    text-align: center;
}}

.metric-label {{
    font-size: 0.8rem;
    color: #94a3b8;
    font-weight: 700;
}}

.metric-value {{
    font-size: 1.2rem;
    font-weight: 800;
    margin-top: 6px;
    color: #38bdf8;
}}

.summary-box {{
    background: rgba(2, 6, 23, 0.85);
    border-radius: 14px;
    padding: 18px;
    border: 1px solid rgba(234, 179, 8, 0.2);
    margin-bottom: 12px;
    min-height: 160px;
}}

.category-icon-title {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}}

.category-icon-title img {{
    width: 32px;
    height: 32px;
    object-fit: contain;
}}

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# GOOGLE SHEETS CONNECTION
# ---------------------------------------------------------
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
    st.stop()

def load_data(worksheet):
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

st.sidebar.markdown('<h2 class="gradient-header">📌 MENU UTAMA</h2>', unsafe_allow_html=True)
menu = st.sidebar.radio("", [
    "📖 Timeline Progress Bulanan",
    "📝 Input Progress Mingguan",
    "🎯 Upload Foto & Evaluasi Bulanan",
    "⚙️ Kelola Metrik & Kategori Baru"
])

def get_latest_finance_val(df_log, bulan_target, metrik_keyword):
    if df_log.empty or "Metrik / Nama Kegiatan" not in df_log.columns:
        return 0
    df_met = df_log[df_log["Metrik / Nama Kegiatan"].str.contains(metrik_keyword, case=False, na=False)]
    if df_met.empty:
        return 0
    df_curr = df_met[df_met["Bulan"] == bulan_target]
    if not df_curr.empty and (df_curr["Nilai"] > 0).any():
        return df_curr[df_curr["Nilai"] > 0]["Nilai"].iloc[-1]
    df_nonzero = df_met[df_met["Nilai"] > 0]
    if not df_nonzero.empty:
        return df_nonzero["Nilai"].iloc[-1]
    return 0

# ---------------------------------------------------------
# 1. TIMELINE PROGRESS BULANAN
# ---------------------------------------------------------
if menu == "📖 Timeline Progress Bulanan":
    st.markdown('<h1 class="gradient-header" style="font-size: 2.2rem; text-align: center;">⚔️ JURNAL & TIMELINE PERKEMBANGAN DIRI ⚔️</h1>', unsafe_allow_html=True)

    df_log = load_data(ws_log)
    df_b = load_data(ws_bulanan)

    daftar_bulan_standar = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                            "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    
    bulan_list = []
    if not df_log.empty and "Bulan" in df_log.columns:
        bulan_list = [b for b in daftar_bulan_standar if b in df_log["Bulan"].unique()]

    if not df_b.empty and "Bulan" in df_b.columns:
        for b in df_b["Bulan"].unique():
            if b not in bulan_list and b in daftar_bulan_standar:
                bulan_list.append(b)

    if not bulan_list:
        st.info("✨ Belum ada data. Mulai dari menu 'Input Progress Mingguan' atau 'Upload Foto & Evaluasi Bulanan'!")
    else:
        for bulan_item in reversed(bulan_list):
            st.markdown(f'<div class="timeline-badge">📅 LAPORAN PERKEMBANGAN — BULAN {bulan_item.upper()}</div>', unsafe_allow_html=True)
            
            # Default foto jika user belum upload
            foto_bulan = "https://i.ibb.co/MBtjqXQ/no-avatar.png"
            evaluasi_text = "Belum ada catatan evaluasi khusus untuk bulan ini."
            
            if not df_b.empty and "Bulan" in df_b.columns:
                df_b_filter = df_b[df_b["Bulan"] == bulan_item]
                if not df_b_filter.empty:
                    row_b = df_b_filter.iloc[-1]
                    evaluasi_text = row_b.get('Evaluasi Umum & Catatan', evaluasi_text)
                    if row_b.get('Foto_URL') and str(row_b.get('Foto_URL')).strip() != "":
                        foto_bulan = str(row_b.get('Foto_URL')).strip()

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            col_avatar, col_info, col_hero = st.columns([1.3, 2.7, 1], gap="medium")
            
            with col_avatar:
                # Foto Diri Diperbesar Pas di Dalam Frame
                st.markdown(f"""
                <div class="avatar-box">
                    <img src="{foto_bulan}" class="user-photo">
                    <img src="{IMG_FRAME}" class="frame-overlay">
                </div>
                """, unsafe_allow_html=True)
                
            with col_info:
                st.markdown('<h2 class="gradient-header" style="margin-bottom: 2px;">Dede Suhendra</h2>', unsafe_allow_html=True)
                st.markdown(f'<p style="color: #eab308; font-weight: 700;">Laporan Perkembangan Diri — Bulan {bulan_item}</p>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.85); border-left: 4px solid #eab308; padding: 14px; border-radius: 12px;">
                    <span style="color: #f43f5e; font-weight: 700;">💡 EVALUASI & CATATAN DIRI:</span><br>
                    <span style="color: #e2e8f0; font-style: italic;">"{evaluasi_text}"</span>
                </div>
                """, unsafe_allow_html=True)

            with col_hero:
                # Hero Masha Tanpa Background
                st.markdown(f'<img src="{IMG_HERO_MAIN}" class="hero-img-display">', unsafe_allow_html=True)

            # REKAPAN OTOMATIS BULANAN
            st.markdown('<h3 style="color: #eab308; font-size: 1.1rem; margin-top: 25px;">📊 REKAPAN TOTAL PENCAPAIAN BULAN INI (OTOMATIS)</h3>', unsafe_allow_html=True)
            
            if not df_log.empty and "Bulan" in df_log.columns:
                df_month = df_log[df_log["Bulan"] == bulan_item]
                
                if not df_month.empty:
                    df_sum = df_month.groupby(["Kategori", "Metrik / Nama Kegiatan", "Satuan"])["Nilai"].sum().reset_index()
                    
                    col_p, col_a, col_k = st.columns(3)
                    
                    with col_p:
                        st.markdown(f"""
                        <div class="summary-box">
                            <div class="category-icon-title">
                                <img src="{IMG_ICON_PENG}">
                                <h4 style="color:#38bdf8; margin:0;">Pengetahuan</h4>
                            </div>
                        """, unsafe_allow_html=True)
                        df_peng = df_sum[df_sum["Kategori"] == "Pengetahuan"]
                        if not df_peng.empty:
                            for _, r in df_peng.iterrows():
                                if r['Nilai'] > 0:
                                    st.markdown(f"• **{r['Metrik / Nama Kegiatan']}**: {r['Nilai']} {r['Satuan']}")
                        else:
                            st.write("Belum ada data.")
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col_a:
                        st.markdown(f"""
                        <div class="summary-box">
                            <div class="category-icon-title">
                                <img src="{IMG_ICON_AGAMA}">
                                <h4 style="color:#4ade80; margin:0;">Agama & Amalan</h4>
                            </div>
                        """, unsafe_allow_html=True)
                        df_agm = df_sum[df_sum["Kategori"] == "Agama"]
                        if not df_agm.empty:
                            for _, r in df_agm.iterrows():
                                if r['Nilai'] > 0:
                                    st.markdown(f"• **{r['Metrik / Nama Kegiatan']}**: {r['Nilai']} {r['Satuan']}")
                        else:
                            st.write("Belum ada data.")
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col_k:
                        st.markdown(f"""
                        <div class="summary-box">
                            <div class="category-icon-title">
                                <img src="{IMG_ICON_KES}">
                                <h4 style="color:#f43f5e; margin:0;">Kesehatan</h4>
                            </div>
                        """, unsafe_allow_html=True)
                        df_kes = df_sum[df_sum["Kategori"] == "Kesehatan"]
                        if not df_kes.empty:
                            for _, r in df_kes.iterrows():
                                if r['Nilai'] > 0:
                                    st.markdown(f"• **{r['Metrik / Nama Kegiatan']}**: {r['Nilai']} {r['Satuan']}")
                        else:
                            st.write("Belum ada data.")
                        st.markdown('</div>', unsafe_allow_html=True)

            # POSISI KEUANGAN
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin-top:25px; margin-bottom:15px;">
                <img src="{IMG_ICON_KEU}" style="width:28px; height:28px;">
                <h3 style="color: #38bdf8; font-size: 1.1rem; margin:0;">POSISI KEUANGAN REAL-TIME (CARRY OVER)</h3>
            </div>
            """, unsafe_allow_html=True)
            
            s_bank = get_latest_finance_val(df_log, bulan_item, "Bank")
            s_dana = get_latest_finance_val(df_log, bulan_item, "DANA")
            s_cash = get_latest_finance_val(df_log, bulan_item, "Cash")
            s_piutang = get_latest_finance_val(df_log, bulan_item, "Piutang")
            s_utang = get_latest_finance_val(df_log, bulan_item, "Utang Saya")

            total_aset = s_bank + s_dana + s_cash + s_piutang
            net_worth = total_aset - s_utang

            m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)
            
            with m_col1:
                st.markdown(f'<div class="metric-box"><div class="metric-label">💳 BANK</div><div class="metric-value">Rp {s_bank:,.0f}</div></div>', unsafe_allow_html=True)
            with m_col2:
                st.markdown(f'<div class="metric-box"><div class="metric-label">📱 DANA</div><div class="metric-value">Rp {s_dana:,.0f}</div></div>', unsafe_allow_html=True)
            with m_col3:
                st.markdown(f'<div class="metric-box"><div class="metric-label">💵 CASH</div><div class="metric-value">Rp {s_cash:,.0f}</div></div>', unsafe_allow_html=True)
            with m_col4:
                st.markdown(f'<div class="metric-box"><div class="metric-label">🤝 PIUTANG</div><div class="metric-value">Rp {s_piutang:,.0f}</div></div>', unsafe_allow_html=True)
            with m_col5:
                st.markdown(f'<div class="metric-box" style="border-color: rgba(244, 63, 94, 0.4);"><div class="metric-label" style="color:#f43f5e;">⚠️ UTANG</div><div class="metric-value" style="color:#f43f5e;">Rp {s_utang:,.0f}</div></div>', unsafe_allow_html=True)
            with m_col6:
                st.markdown(f'<div class="metric-box" style="background: linear-gradient(135deg, rgba(217, 119, 6, 0.3), rgba(234, 179, 8, 0.3)); border-color: #eab308;"><div class="metric-label" style="color:#fff;">👑 NET WORTH</div><div class="metric-value" style="color:#4ade80;">Rp {net_worth:,.0f}</div></div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<hr style="border:0; height:1px; background: rgba(234, 179, 8, 0.3); margin: 30px 0;">', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INPUT PROGRESS MINGGUAN
# ---------------------------------------------------------
elif menu == "📝 Input Progress Mingguan":
    st.markdown('<h2 class="gradient-header">📝 INPUT PROGRESS MINGGUAN</h2>', unsafe_allow_html=True)

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
            {"Kategori": "Keuangan", "Nama Metrik": "Piutang (Diutangin)", "Satuan": "Rp"},
            {"Kategori": "Keuangan", "Nama Metrik": "Utang Saya", "Satuan": "Rp"}
        ]
        ws_custom.append_rows([list(d.values()) for d in default_metrics])
        df_custom = load_data(ws_custom)

    with st.form("form_mingguan"):
        col1, col2 = st.columns(2)
        with col1:
            bulan = st.selectbox("Pilih Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                                                "Juli", "Agustus", "September", "Oktober", "November", "Desember"], index=7)
        with col2:
            minggu = st.selectbox("Pilih Minggu", ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"])
        
        st.divider()
        
        input_data = []
        kategori_list = df_custom["Kategori"].unique() if "Kategori" in df_custom.columns else []

        for kat in kategori_list:
            st.markdown(f'<h3 style="color:#eab308; margin-top:15px;">🔹 Kategori: {kat}</h3>', unsafe_allow_html=True)
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
                    catatan = st.text_input(f"Catatan {metrik_nama}", key=f"note_{bulan}_{minggu}_{metrik_nama}")
                
                input_data.append([bulan, minggu, kat, metrik_nama, nilai, satuan, catatan])

        submit_btn = st.form_submit_button("🚀 SIMPAN DATA MINGGUAN")

    if submit_btn:
        with st.spinner("Menyimpan ke Google Sheets..."):
            ws_log.append_rows(input_data)
            st.success(f"🎉 Data minggu ini untuk bulan {bulan} berhasil disimpan!")

# ---------------------------------------------------------
# 3. INPUT EVALUASI & FOTO BULANAN
# ---------------------------------------------------------
elif menu == "🎯 Upload Foto & Evaluasi Bulanan":
    st.markdown('<h2 class="gradient-header">🎯 UPLOAD FOTO & EVALUASI DIRI BULANAN</h2>', unsafe_allow_html=True)

    with st.form("form_bulanan"):
        bulan_eval = st.selectbox("Pilih Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                                                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"], index=7)
        
        foto_url_input = st.text_input("Link Foto ImgBB Bulan Ini (Direct Link .jpg/.png):", placeholder="https://i.ibb.co/xxxx/foto.jpg")
        evaluasi_umum = st.text_area("Evaluasi Umum & Catatan Diri Bulan Ini", placeholder="Refleksi dan catatan hal yang perlu ditingkatkan bulan depan...")

        submit_bulanan = st.form_submit_button("🚀 SIMPAN JURNAL BULANAN")

    if submit_bulanan:
        with st.spinner("Menyimpan ke Google Sheets..."):
            row_bulanan = [bulan_eval, "", "", "", "", evaluasi_umum, foto_url_input]
            ws_bulanan.append_row(row_bulanan)
            st.success(f"🎉 Foto & Evaluasi bulan {bulan_eval} berhasil disimpan!")

# ---------------------------------------------------------
# 4. KELOLA METRIK BARU
# ---------------------------------------------------------
elif menu == "⚙️ Kelola Metrik & Kategori Baru":
    st.markdown('<h2 class="gradient-header">⚙️ TAMBAH METRIK / KATEGORI BARU</h2>', unsafe_allow_html=True)

    df_custom = load_data(ws_custom)
    
    with st.form("form_tambah_metrik"):
        kat_baru = st.text_input("Nama Kategori", placeholder="Misal: Side Project, Hobi...")
        metrik_baru = st.text_input("Nama Metrik / Kegiatan", placeholder="Misal: Jam Coding, Target Belajar...")
        satuan_baru = st.text_input("Satuan", placeholder="Misal: Jam, Menit, Reps, Rp...")
        
        submit_custom = st.form_submit_button("➕ TAMBAH PARAMETER")

    if submit_custom:
        if kat_baru and metrik_baru and satuan_baru:
            ws_custom.append_row([kat_baru, metrik_baru, satuan_baru])
            st.success(f"✅ Parameter '{metrik_baru}' berhasil ditambahkan!")
            st.rerun()

    st.divider()
    st.dataframe(df_custom, use_container_width=True)
