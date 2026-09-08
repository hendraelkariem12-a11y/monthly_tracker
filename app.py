import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# CONFIG & PAGE SETUP
# ---------------------------------------------------------
st.set_page_config(
    page_title="Monthly Progress & Finance Journal",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM INJECTED CSS (ANIMATIONS, GRADIENTS, GLASSMORPHISM)
# ---------------------------------------------------------
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');

/* Global Font & Background Styling */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    color: #f8fafc;
}

/* Keyframe Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.4); }
    50% { box-shadow: 0 0 30px rgba(168, 85, 247, 0.7); }
    100% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.4); }
}

@keyframes floatAnim {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(30, 41, 59, 0.7) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
    animation: fadeIn 0.8s ease-out forwards;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    transform: translateY(-5px);
    border-color: rgba(168, 85, 247, 0.4);
    box-shadow: 0 12px 30px -10px rgba(168, 85, 247, 0.3);
}

/* Gradient Text Headers */
.gradient-header {
    background: linear-gradient(90deg, #38bdf8 0%, #a855f7 50%, #f43f5e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.timeline-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 9999px;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    box-shadow: 0 4px 14px rgba(168, 85, 247, 0.4);
    animation: pulseGlow 3s infinite;
    margin-bottom: 12px;
}

/* Custom Metric Card Style */
.metric-box {
    background: rgba(15, 23, 42, 0.6);
    border-radius: 16px;
    padding: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    text-align: center;
    transition: transform 0.2s ease;
}

.metric-box:hover {
    transform: scale(1.03);
    background: rgba(30, 41, 59, 0.8);
}

.metric-label {
    font-size: 0.82rem;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-value {
    font-size: 1.2rem;
    font-weight: 800;
    margin-top: 6px;
    color: #38bdf8;
}

/* Photo Frame Animation */
.photo-frame {
    border-radius: 20px;
    overflow: hidden;
    border: 2px solid rgba(168, 85, 247, 0.5);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
    animation: floatAnim 4s ease-in-out infinite;
}

/* Streamlit Native UI Overrides */
div[data-baseweb="select"] > div {
    background-color: rgba(30, 41, 59, 0.8) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: white !important;
}

.stButton > button {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 25px rgba(168, 85, 247, 0.6) !important;
}

button[data-baseweb="tab"] {
    font-weight: 700 !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
}

button[aria-selected="true"] {
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2)) !important;
    color: #38bdf8 !important;
    border-bottom: 2px solid #a855f7 !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
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
    st.error(f"⚠️ Gagal terhubung ke Google Sheets: {e}")
    st.info("Pastikan Secrets st.secrets['gcp_service_account'] terpasang dengan benar di Streamlit Cloud.")
    st.stop()

def load_data(worksheet):
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.markdown('<h2 class="gradient-header">⚡ NAVIGATION</h2>', unsafe_allow_html=True)
menu = st.sidebar.radio("", [
    "📖 Timeline Progress Bulanan",
    "📝 Input Progress Mingguan",
    "🎯 Input Evaluasi & Foto Bulanan",
    "⚙️ Kelola Metrik & Kategori Baru"
])

# HELPER SALDO TERAKHIR (CARRY OVER KEUANGAN)
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
# 1. TIMELINE PROGRESS BULANAN (ANIMATED DASHBOARD)
# ---------------------------------------------------------
if menu == "📖 Timeline Progress Bulanan":
    st.markdown('<h1 class="gradient-header" style="font-size: 2.2rem; text-align: center; margin-bottom: 0px;">✨ PERSONAL JOURNAL & TIMELINE ✨</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 0.95rem; margin-bottom: 30px;">Visualisasi perkembangan fisik, finansial, dan amalan dari bulan ke bulan.</p>', unsafe_allow_html=True)

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
        st.info("✨ Belum ada data yang tersimpan. Mulai isi jurnal dari menu sidebar!")
    else:
        for bulan_item in reversed(bulan_list):
            st.markdown(f'<div class="timeline-badge">📅 LAPORAN PERKEMBANGAN — BULAN {bulan_item.upper()}</div>', unsafe_allow_html=True)
            
            foto_bulan = "https://via.placeholder.com/400x500?text=Foto+Diri+Bulan+Ini"
            evaluasi_text = "Belum ada catatan evaluasi untuk bulan ini."
            
            if not df_b.empty and "Bulan" in df_b.columns:
                df_b_filter = df_b[df_b["Bulan"] == bulan_item]
                if not df_b_filter.empty:
                    row_b = df_b_filter.iloc[-1]
                    evaluasi_text = row_b.get('Evaluasi Umum & Catatan', evaluasi_text)
                    if row_b.get('Foto_URL') and str(row_b.get('Foto_URL')).strip() != "":
                        foto_bulan = str(row_b.get('Foto_URL')).strip()

            # Glass Card Layout
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            col_img, col_info = st.columns([1, 2], gap="large")
            
            with col_img:
                st.markdown('<div class="photo-frame">', unsafe_allow_html=True)
                st.image(foto_bulan, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_info:
                st.markdown('<h2 class="gradient-header" style="margin-bottom: 4px;">Dede Suhendra</h2>', unsafe_allow_html=True)
                st.markdown(f'<p style="color: #a855f7; font-weight: 600;">Status: Aktif Membangun Diri ({bulan_item})</p>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.7); border-left: 4px solid #a855f7; padding: 16px; border-radius: 12px; margin-top: 15px;">
                    <span style="color: #f43f5e; font-weight: 700;">💡 EVALUASI & CATATAN DIRI:</span><br>
                    <span style="color: #e2e8f0; font-style: italic;">"{evaluasi_text}"</span>
                </div>
                """, unsafe_allow_html=True)

            # FINANSIAL DASHBOARD (NEON METRICS)
            st.markdown('<h3 style="color: #38bdf8; font-size: 1.1rem; margin-top: 25px; margin-bottom: 15px;">💎 POSISI KEUANGAN REAL-TIME (CARRY OVER)</h3>', unsafe_allow_html=True)
            
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
                st.markdown(f'<div class="metric-box" style="border-color: rgba(244, 63, 94, 0.3);"><div class="metric-label" style="color:#f43f5e;">⚠️ UTANG</div><div class="metric-value" style="color:#f43f5e;">Rp {s_utang:,.0f}</div></div>', unsafe_allow_html=True)
            with m_col6:
                st.markdown(f'<div class="metric-box" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3)); border-color: #a855f7;"><div class="metric-label" style="color:#fff;">👑 NET WORTH</div><div class="metric-value" style="color:#4ade80;">Rp {net_worth:,.0f}</div></div>', unsafe_allow_html=True)

            st.markdown('<br>', unsafe_allow_html=True)

            # DETAIL AKTIVITAS NON-KEUANGAN
            if not df_log.empty and "Bulan" in df_log.columns:
                df_filtered = df_log[(df_log["Bulan"] == bulan_item) & (df_log["Kategori"] != "Keuangan")]
                
                with st.expander(f"📊 DETAIL PENCAPAIAN MINGGUAN ({bulan_item.upper()})"):
                    t1, t2, t3 = st.tabs(["🧠 PENGETAHUAN", "🕌 AGAMA & AMALAN", "🏃 KESEHATAN"])
                    
                    with t1:
                        st.dataframe(df_filtered[df_filtered["Kategori"] == "Pengetahuan"][["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)
                    with t2:
                        st.dataframe(df_filtered[df_filtered["Kategori"] == "Agama"][["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)
                    with t3:
                        st.dataframe(df_filtered[df_filtered["Kategori"] == "Kesehatan"][["Minggu", "Metrik / Nama Kegiatan", "Nilai", "Satuan", "Catatan"]], use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<hr style="border:0; height:1px; background: linear-gradient(90deg, transparent, rgba(168, 85, 247, 0.5), transparent); margin: 40px 0;">', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INPUT PROGRESS MINGGUAN
# ---------------------------------------------------------
elif menu == "📝 Input Progress Mingguan":
    st.markdown('<h2 class="gradient-header">📝 INPUT PROGRESS MINGGUAN</h2>', unsafe_allow_html=True)
    st.write("Isi perkembangan mingguan kamu. Data otomatis tersimpan secara permanen di Google Sheets.")

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
                                                "Juli", "Agustus", "September", "Oktober", "November", "Desember"], index=8)
        with col2:
            minggu = st.selectbox("Pilih Minggu", ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"])
        
        st.divider()
        
        input_data = []
        kategori_list = df_custom["Kategori"].unique() if "Kategori" in df_custom.columns else []

        for kat in kategori_list:
            st.markdown(f'<h3 style="color:#a855f7; margin-top:15px;">🔹 Kategori: {kat}</h3>', unsafe_allow_html=True)
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
elif menu == "🎯 Input Evaluasi & Foto Bulanan":
    st.markdown('<h2 class="gradient-header">🎯 EVALUASI & FOTO DIRI BULANAN</h2>', unsafe_allow_html=True)

    with st.form("form_bulanan"):
        bulan_eval = st.selectbox("Pilih Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                                                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"], index=8)
        
        foto_url_input = st.text_input("Link Foto ImgBB Bulan Ini (Direct Link .jpg/.png):", placeholder="https://i.ibb.co/xxxx/foto.jpg")
        
        pengetahuan_eval = st.text_area("Pencapaian Pengetahuan", placeholder="Buku yang dibaca, bahasa yang dikuasai...")
        agama_eval = st.text_area("Pencapaian Agama", placeholder="Perkembangan amalan, hafalan, dan ibadah...")
        kesehatan_eval = st.text_area("Pencapaian Kesehatan", placeholder="Perkembangan stamina, jogging, dan latihan fisik...")
        keuangan_eval = st.text_area("Pencapaian Keuangan", placeholder="Perkembangan aset, tabungan, dan rencana finansial...")
        evaluasi_umum = st.text_area("Evaluasi Umum & Pesan Diri", placeholder="Refleksi dan apa yang perlu ditingkatkan bulan depan...")

        submit_bulanan = st.form_submit_button("🚀 SIMPAN JURNAL BULANAN")

    if submit_bulanan:
        with st.spinner("Menyimpan ke Google Sheets..."):
            row_bulanan = [bulan_eval, pengetahuan_eval, agama_eval, kesehatan_eval, keuangan_eval, evaluasi_umum, foto_url_input]
            ws_bulanan.append_row(row_bulanan)
            st.success(f"🎉 Jurnal & Foto untuk bulan {bulan_eval} berhasil disimpan!")

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
            st.success(f"✅ Metrik '{metrik_baru}' berhasil ditambahkan!")
            st.rerun()

    st.divider()
    st.dataframe(df_custom, use_container_width=True)
