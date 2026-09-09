import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# ---------------------------------------------------------
# CONFIG & PAGE SETUP
# ---------------------------------------------------------
st.set_page_config(
    page_title="Jurnal Perjalanan Diri",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ASSET LINKS
# ---------------------------------------------------------
IMG_FRAME = "https://i.ibb.co.com/Pzgqj1wD/1788849011671-removebg-preview.png"
IMG_ICON_PENG = "https://i.ibb.co.com/pjSJJXgJ/1788848846642-removebg-preview.png"
IMG_ICON_AGAMA = "https://i.ibb.co.com/wrKqkpqf/1788849113579-removebg-preview.png"
IMG_ICON_KES = "https://i.ibb.co.com/zhm13rJD/1788849195681-removebg-preview.png"
IMG_ICON_KEU = "https://i.ibb.co.com/2YpL6vjZ/1788849240997-removebg-preview.png"
IMG_PLACEHOLDER = "https://i.ibb.co/MBtjqXQ/no-avatar.png"

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700;800&family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top right, #1e1b4b, #0f172a 60%, #020617 100%);
    color: #f8fafc;
}

.glass-card {
    background: rgba(15, 23, 42, 0.75) !important;
    backdrop-filter: blur(14px);
    border: 1px solid rgba(234, 179, 8, 0.25);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
}

.gradient-header {
    font-family: 'Rajdhani', sans-serif;
    background: linear-gradient(90deg, #38bdf8 0%, #eab308 50%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

.timeline-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 9999px;
    background: linear-gradient(90deg, #d97706, #eab308);
    color: #020617;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 800;
    margin-bottom: 16px;
}

.avatar-box {
    position: relative;
    width: 160px;
    height: 160px;
    margin: 0 auto;
}

.user-photo {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    object-fit: cover;
    position: absolute;
    top: 25px;
    left: 25px;
    z-index: 1;
}

.frame-overlay {
    width: 160px;
    height: 160px;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 2;
    pointer-events: none;
    object-fit: contain;
}

.photo-gallery {
    display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px;
}

.gallery-photo {
    width: 90px; height: 90px; border-radius: 12px; object-fit: cover;
    border: 2px solid rgba(234, 179, 8, 0.3); transition: transform 0.2s;
}
.gallery-photo:hover { transform: scale(1.05); }

.metric-box {
    background: rgba(30, 41, 59, 0.6); border-radius: 16px; padding: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08); text-align: center; transition: transform 0.2s;
}
.metric-box:hover { transform: translateY(-2px); }
.metric-label { font-size: 0.78rem; color: #94a3b8; font-weight: 700; }
.metric-value { font-size: 1rem; font-weight: 800; margin-top: 4px; }
.change-up { color: #4ade80; font-size: 0.7rem; margin-top: 2px; }
.change-down { color: #f43f5e; font-size: 0.7rem; margin-top: 2px; }

.summary-box {
    background: rgba(2, 6, 23, 0.85); border-radius: 14px; padding: 18px;
    border: 1px solid rgba(234, 179, 8, 0.2); margin-bottom: 12px; min-height: 120px; transition: border-color 0.2s;
}
.summary-box:hover { border-color: rgba(234, 179, 8, 0.4); }

.category-icon-title { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.category-icon-title img { width: 32px; height: 32px; object-fit: contain; }
.note-text { color: #94a3b8; font-size: 0.85rem; font-style: italic; margin-top: 4px; margin-bottom: 10px; padding-left: 10px; border-left: 2px solid #38bdf8; }
.divider-line { height: 1px; background: linear-gradient(90deg, transparent, rgba(234, 179, 8, 0.3), transparent); margin: 16px 0; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
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
    return gspread.authorize(creds)

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

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def get_monthly_balance(df_log, bulan_target, keyword):
    if df_log.empty or "Metrik / Nama Kegiatan" not in df_log.columns:
        return 0
    df_keuangan = df_log[df_log["Kategori"].isin(["Keuangan", "Dompet", "Investasi"])]
    if df_keuangan.empty:
        return 0
    df_item = df_keuangan[df_keuangan["Metrik / Nama Kegiatan"].astype(str).str.contains(keyword, case=False, na=False)]
    if df_item.empty:
        return 0
    bulan_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    idx_target = bulan_list.index(bulan_target)
    bulan_sampai = bulan_list[:idx_target + 1]
    df_sampai = df_item[df_item["Bulan"].isin(bulan_sampai)]
    if df_sampai.empty:
        return 0
    df_saldo_input = df_sampai[~df_sampai["Metrik / Nama Kegiatan"].astype(str).str.contains("Pengeluaran", case=False, na=False)]
    saldo = 0 if df_saldo_input.empty or (df_saldo_input["Nilai"] <= 0).all() else df_saldo_input[df_saldo_input["Nilai"] > 0]["Nilai"].iloc[-1]
    df_pengeluaran = df_sampai[df_sampai["Metrik / Nama Kegiatan"].astype(str).str.contains("Pengeluaran", case=False, na=False)]
    total_pengeluaran = df_pengeluaran["Nilai"].sum() if not df_pengeluaran.empty else 0
    return max(0, saldo - total_pengeluaran)

def get_previous_month(bulan_name):
    bulan_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    idx = bulan_list.index(bulan_name)
    return bulan_list[idx - 1] if idx > 0 else None

def format_rp(value):
    return f"Rp {value:,.0f}".replace(",", ".")

def change_html(current, previous):
    if previous == 0: return ""
    diff = current - previous
    if diff > 0:
        return f'<div class="change-up">📈 +{format_rp(diff)}</div>'
    elif diff < 0:
        return f'<div class="change-down">📉 -{format_rp(abs(diff))}</div>'
    return ""

# ---------------------------------------------------------
# SIDEBAR & NAVIGATION
# ---------------------------------------------------------
st.sidebar.markdown('<h2 class="gradient-header">📌 MENU UTAMA</h2>', unsafe_allow_html=True)
menu = st.sidebar.radio("", [
    "📖 Timeline Progress Bulanan",
    "📝 Input Progress Mingguan",
    "💸 Catat Pengeluaran",
    "🎯 Foto & Refleksi Bulanan",
    "⚙️ Kelola Kategori & Metrik"
])

# ---------------------------------------------------------
# 1. TIMELINE PROGRESS BULANAN — DENGAN PILIHAN BULAN
# ---------------------------------------------------------
if menu == "📖 Timeline Progress Bulanan":
    st.markdown('<h1 class="gradient-header" style="font-size: 2.2rem; text-align: center;">🚀 PERJALANANKU — TIMELINE PROGRESS</h1>', unsafe_allow_html=True)

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
                bulan_list.append(bulan_list.append(b) or b)

    if not bulan_list:
        st.info("✨ Belum ada data. Mulai dari menu 'Input Progress Mingguan' untuk memulai perjalananmu!")
    else:
        st.markdown("#### 📅 Pilih Bulan yang Ingin Dilihat")
        pilihan_bulan = ["📂 Semua Bulan"] + list(reversed(bulan_list))
        pilihan_dipilih = st.selectbox("", pilihan_bulan, label_visibility="collapsed")
        st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

        bulan_tampil = list(reversed(bulan_list)) if pilihan_dipilih == "📂 Semua Bulan" else [pilihan_dipilih]

        for bulan_item in bulan_tampil:
            st.markdown(f'<div class="timeline-badge">📅 LAPORAN — BULAN {bulan_item.upper()}</div>', unsafe_allow_html=True)
            
            foto_urls = []
            evaluasi_text = ""
            if not df_b.empty and "Bulan" in df_b.columns:
                df_b_filter = df_b[df_b["Bulan"] == bulan_item]
                if not df_b_filter.empty:
                    row_b = df_b_filter.iloc[-1]
                    evaluasi_text = row_b.get('Evaluasi Umum & Catatan', "")
                    foto_str = str(row_b.get('Foto_URL', '')).strip()
                    if foto_str and foto_str != "":
                        foto_urls = [f.strip() for f in foto_str.split(",") if f.strip() != ""]

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            col_left, col_main = st.columns([1, 3], gap="medium")
            
            with col_left:
                st.markdown(f"""
                <div class="avatar-box">
                    <img src="{foto_urls[0] if foto_urls else IMG_PLACEHOLDER}" class="user-photo">
                    <img src="{IMG_FRAME}" class="frame-overlay">
                </div>
                """, unsafe_allow_html=True)
                st.markdown('<div style="text-align: center; margin-top: 8px;">', unsafe_allow_html=True)
                st.markdown('<h3 class="gradient-header" style="margin: 0; font-size: 1.3rem;">Dede Suhendra</h3>', unsafe_allow_html=True)
                st.markdown(f'<p style="color: #eab308; font-weight: 600; font-size: 0.9rem;">Bulan {bulan_item}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_main:
                st.markdown("#### ✍️ Refleksi Bulan Ini")
                if evaluasi_text:
                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.85); border-left: 4px solid #eab308; padding: 14px; border-radius: 12px;">
                    <span style="color: #e2e8f0;">{evaluasi_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: rgba(15, 23, 42, 0.5); border-left: 3px solid #475569; padding: 14px; border-radius: 12px; color: #94a3b8; font-style: italic;">
                    💡 Belum ada refleksi bulan ini. Yuk tuliskan di menu <strong>"Foto & Refleksi Bulanan"</strong> ✨
                    </div>
                    """, unsafe_allow_html=True)
                if foto_urls:
                    st.markdown("#### 📸 Momen Bulan Ini")
                    foto_html = '<div class="photo-gallery">'
                    for url in foto_urls[:4]:
                        foto_html += f'<img src="{url}" class="gallery-photo" alt="foto bulan">'
                    foto_html += '</div>'
                    st.markdown(foto_html, unsafe_allow_html=True)

            st.markdown('<h3 style="color: #eab308; font-size: 1.1rem; margin-top: 25px;">📊 PERTUMBUHAN & PENCAPAIAN</h3>', unsafe_allow_html=True)
            prev_bulan = get_previous_month(bulan_item)
            if not df_log.empty and "Bulan" in df_log.columns:
                df_month = df_log[df_log["Bulan"] == bulan_item]
                df_prev = df_log[df_log["Bulan"] == prev_bulan] if prev_bulan is not None else pd.DataFrame()
                if not df_month.empty:
                    col_p, col_a, col_k = st.columns(3)
                    with col_p:
                        html_peng = '<div class="summary-box"><div class="category-icon-title">' + f'<img src="{IMG_ICON_PENG}"><h4 style="color:#38bdf8; margin:0;">Pengetahuan</h4></div>'
                        df_peng = df_month[df_month["Kategori"] == "Pengetahuan"]
                        df_peng_prev = df_prev[df_prev["Kategori"] == "Pengetahuan"] if not df_prev.empty else pd.DataFrame()
                        if not df_peng.empty:
                            for metrik, grp in df_peng.groupby("Metrik / Nama Kegiatan"):
                                tot_val = grp["Nilai"].sum()
                                satuan = grp["Satuan"].iloc[0]
                                prev_val = df_peng_prev[df_peng_prev["Metrik / Nama Kegiatan"] == metrik]["Nilai"].sum() if not df_peng_prev.empty else 0
                                html_peng += f"<p style='margin-bottom:4px;'>• <b>{metrik}</b>: <code>{tot_val}</code> {satuan}"
                                if prev_val > 0:
                                    diff = tot_val - prev_val
                                    html_peng += f" <span style='color:#4ade80; font-size:0.8rem;'>(↑ {diff})</span>" if diff > 0 else f" <span style='color:#f43f5e; font-size:0.8rem;'>(↓ {abs(diff)})</span>" if diff < 0 else ""
                                html_peng += "</p>"
                                notes = [str(n).strip() for n in grp["Catatan"].tolist() if str(n).strip() != ""]
                                if notes: html_peng += f'<div class="note-text">{", ".join(notes)}</div>'
                        else:
                            html_peng += "<p style='color:#64748b; font-style:italic;'>Belum ada data bulan ini.</p>"
                        html_peng += "</div>"
                        st.markdown(html_peng, unsafe_allow_html=True)

                    with col_a:
                        html_agm = '<div class="summary-box"><div class="category-icon-title">' + f'<img src="{IMG_ICON_AGAMA}"><h4 style="color:#4ade80; margin:0;">Agama & Amalan</h4></div>'
                        df_agm = df_month[df_month["Kategori"] == "Agama"]
                        df_agm_prev = df_prev[df_prev["Kategori"] == "Agama"] if not df_prev.empty else pd.DataFrame()
                        if not df_agm.empty:
                            for metrik, grp in df_agm.groupby("Metrik / Nama Kegiatan"):
                                tot_val = grp["Nilai"].sum()
                                satuan = grp["Satuan"].iloc[0]
                                prev_val = df_agm_prev[df_agm_prev["Metrik / Nama Kegiatan"] == metrik]["Nilai"].sum() if not df_agm_prev.empty else 0
                                html_agm += f"<p style='margin-bottom:4px;'>• <b>{metrik}</b>: <code>{tot_val}</code> {satuan}"
                                if prev_val > 0:
                                    diff = tot_val - prev_val
                                    html_agm += f" <span style='color:#4ade80; font-size:0.8rem;'>(↑ {diff})</span>" if diff > 0 else f" <span style='color:#f43f5e; font-size:0.8rem;'>(↓ {abs(diff)})</span>" if diff < 0 else ""
                                html_agm += "</p>"
                                notes = [str(n).strip() for n in grp["Catatan"].tolist() if str(n).strip() != ""]
                                if notes: html_agm += f'<div class="note-text">{", ".join(notes)}</div>'
                        else:
                            html_agm += "<p style='color:#64748b; font-style:italic;'>Belum ada data bulan ini.</p>"
                        html_agm += "</div>"
                        st.markdown(html_agm, unsafe_allow_html=True)

                    with col_k:
                        html_kes = '<div class="summary-box"><div class="category-icon-title">' + f'<img src="{IMG_ICON_KES}"><h4 style="color:#f43f5e; margin:0;">Kesehatan</h4></div>'
                        df_kes = df_month[df_month["Kategori"] == "Kesehatan"]
                        df_kes_prev = df_prev[df_prev["Kategori"] == "Kesehatan"] if not df_prev.empty else pd.DataFrame()
                        if not df_kes.empty:
                            for metrik, grp in df_kes.groupby("Metrik / Nama Kegiatan"):
                                tot_val = grp["Nilai"].sum()
                                satuan = grp["Satuan"].iloc[0]
                                prev_val = df_kes_prev[df_kes_prev["Metrik / Nama Kegiatan"] == metrik]["Nilai"].sum() if not df_kes_prev.empty else 0
                                html_kes += f"<p style='margin-bottom:4px;'>• <b>{metrik}</b>: <code>{tot_val}</code> {satuan}"
                                if prev_val > 0:
                                    diff = tot_val - prev_val
                                    html_kes += f" <span style='color:#4ade80; font-size:0.8rem;'>(↑ {diff})</span>" if diff > 0 else f" <span style='color:#f43f5e; font-size:0.8rem;'>(↓ {abs(diff)})</span>" if diff < 0 else ""
                                html_kes += "</p>"
                                notes = [str(n).strip() for n in grp["Catatan"].tolist() if str(n).strip() != ""]
                                if notes: html_kes += f'<div class="note-text">{", ".join(notes)}</div>'
                        else:
                            html_kes += "<p style='color:#64748b; font-style:italic;'>Belum ada data bulan ini.</p>"
                        html_kes += "</div>"
                        st.markdown(html_kes, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin-top:30px; margin-bottom:15px;">
                <img src="{IMG_ICON_KEU}" style="width:28px; height:28px;">
                <h3 style="color: #38bdf8; font-size: 1.1rem; margin:0;">💵 DOMPET — BULAN {bulan_item.upper()}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            s_cash = get_monthly_balance(df_log, bulan_item, "Cash|Tunai")
            s_bank = get_monthly_balance(df_log, bulan_item, "^Bank$")
            s_ewallet = get_monthly_balance(df_log, bulan_item, "E-Wallet|DANA|GoPay")
            s_ajaib = get_monthly_balance(df_log, bulan_item, "Ajaib")
            s_cash_prev = get_monthly_balance(df_log, prev_bulan, "Cash|Tunai") if prev_bulan else 0
            s_bank_prev = get_monthly_balance(df_log, prev_bulan, "^Bank$") if prev_bulan else 0
            s_ewallet_prev = get_monthly_balance(df_log, prev_bulan, "E-Wallet|DANA|GoPay") if prev_bulan else 0
            s_ajaib_prev = get_monthly_balance(df_log, prev_bulan, "Ajaib") if prev_bulan else 0

            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
            with col_d1: st.markdown(f'<div class="metric-box"><div class="metric-label">💵 Cash</div><div class="metric-value" style="color:#38bdf8;">{format_rp(s_cash)}</div><div style="font-size:0.7rem; color:#64748b;">Lalu: {format_rp(s_cash_prev)}</div>{change_html(s_cash, s_cash_prev)}</div>', unsafe_allow_html=True)
            with col_d2: st.markdown(f'<div class="metric-box"><div class="metric-label">🏦 Bank</div><div class="metric-value" style="color:#38bdf8;">{format_rp(s_bank)}</div><div style="font-size:0.7rem; color:#64748b;">Lalu: {format_rp(s_bank_prev)}</div>{change_html(s_bank, s_bank_prev)}</div>', unsafe_allow_html=True)
            with col_d3: st.markdown(f'<div class="metric-box"><div class="metric-label">📱 E-Wallet</div><div class="metric-value" style="color:#38bdf8;">{format_rp(s_ewallet)}</div><div style="font-size:0.7rem; color:#64748b;">Lalu: {format_rp(s_ewallet_prev)}</div>{change_html(s_ewallet, s_ewallet_prev)}</div>', unsafe_allow_html=True)
            with col_d4: st.markdown(f'<div class="metric-box"><div class="metric-label">📲 Ajaib</div><div class="metric-value" style="color:#38bdf8;">{format_rp(s_ajaib)}</div><div style="font-size:0.7rem; color:#64748b;">Lalu: {format_rp(s_ajaib_prev)}</div>{change_html(s_ajaib, s_ajaib_prev)}</div>', unsafe_allow_html=True)

            st.markdown('<h3 style="color: #a855f7; font-size: 1.1rem; margin-top:25px; margin-bottom:15px;">📈 ASET INVESTASI</h3>', unsafe_allow_html=True)
            saham = get_monthly_balance(df_log, bulan_item, "Saham")
            reksadana = get_monthly_balance(df_log, bulan_item, "Reksadana")
            forex = get_monthly_balance(df_log, bulan_item, "Forex")
            kripto = get_monthly_balance(df_log, bulan_item, "Kripto")
            saham_prev = get_monthly_balance(df_log, prev_bulan, "Saham") if prev_bulan else 0
            reksadana_prev = get_monthly_balance(df_log, prev_bulan, "Reksadana") if prev_bulan else 0
            forex_prev = get_monthly_balance(df_log, prev_bulan, "Forex") if prev_bulan else 0
            kripto_prev = get_monthly_balance(df_log, prev_bulan, "Kripto") if prev_bulan else 0

            col_i1, col_i2, col_i3, col_i4 = st.columns(4)
            with col_i1: st.markdown(f'<div class="metric-box" style="border-color: rgba(168,85,247,0.2);"><div class="metric-label" style="color:#a855f7;">📊 Saham</div><div class="metric-value" style="color:#a855f7;">{format_rp(saham)}</div><div style="font-size:0.7rem; color:#64748b;">Lalu: {format_rp(saham_prev)}</div>{change_html(saham, saham_prev)}</div>', unsafe_allow_html=True)
            with col_i2: st.markdown(f'<div class="metric-box" style="border-color: rgba(168,85,247,0.2);"><div class="metric-label" style="color:#a855f7;">📊 Reksadana</div><div class="metric-value" style="color:#a855f7;">{format_rp(reksadana)}</div><div style="font-size:0.7rem; color:#64748b;">Lalu: {format_rp(reksadana_prev)}</div>{change_html(reksadana, reksadana_prev)}</div>', unsafe_allow_html=True)
            with col_i3: st.markdown(f'<div class="metric-box" style="border-color: rgba(168,85,247,0.2);"><div class="metric-label" style="color:#a855f7;">📊 Forex</div><div class="metric-value" style="color:#a855f7;">{format_rp(forex)}</div><div style="font-size:0.7rem; color:#64748b;">Lalu: {format_rp(forex_prev)}</div>{change_html(forex, forex_prev)}</div>', unsafe_allow_html=True)
            with col_i4: st.markdown(f'<div class="metric-box" style="border-color: rgba(168,85,247,0.2);"><div class="metric-label" style="color:#a855f7;">🪙 Kripto</div><div class="metric-value" style="color:#a855f7;">{format_rp(kripto)}</div><div style="font-size:0.7rem; color:#64748b;">Lalu: {format_rp(kripto_prev)}</div>{change_html(kripto, kripto_prev)}</div>', unsafe_allow_html=True)

            total_dompet = s_cash + s_bank + s_ewallet + s_ajaib
            total_inv = saham + reksadana + forex + kripto
            total = total_dompet + total_inv
            total_dompet_prev = s_cash_prev + s_bank_prev + s_ewallet_prev + s_ajaib_prev
            total_inv_prev = saham_prev + reksadana_prev + forex_prev + kripto_prev
            total_prev = total_dompet_prev + total_inv_prev
            
            st.markdown(f"""
            <div style="margin-top:20px;">
                <div class="metric-box" style="background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(168,85,247,0.15)); border-color: #eab308;">
                    <div class="metric-label" style="color:#eab308; font-size:0.9rem;">👑 TOTAL KEKAYAAN</div>
                    <div class="metric-value" style="color:#4ade80; font-size:1.4rem;">{format_rp(total)}</div>
                    <div style="font-size:0.8rem; color:#94a3b8;">Bulan lalu: {format_rp(total_prev)}</div>
                    {change_html(total, total_prev)}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<hr style="border:0; height:1px; background: rgba(234,179,8,0.2); margin:24px 0;">', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INPUT PROGRESS MINGGUAN
# ---------------------------------------------------------
elif menu == "📝 Input Progress Mingguan":
    st.markdown('<h2 class="gradient-header">📝 CATAT PROGRESS MINGGUAN</h2>', unsafe_allow_html=True)
    st.write("Pilih kategori, lalu isi pencapaianmu. Lebih rapi, lebih cepat! ✨")

    df_custom = load_data(ws_custom)
    if df_custom.empty:
        default_metrics = [
            ["Pengetahuan", "Artikel Dibaca", "Artikel"],
            ["Pengetahuan", "Belajar B. Inggris", "Menit"],
            ["Pengetahuan", "Belajar B. Arab", "Menit"],
            ["Pengetahuan", "Buku Fisik Dibaca", "Buku"],
            ["Pengetahuan", "E-Book Dibaca", "Buku"],
            ["Pengetahuan", "Catatan / Buku Dibuat", "Buat"],
            ["Pengetahuan", "Hafalan Al-Qur'an", "Surah/Juz"],
            ["Agama", "Salat Dhuha", "Kali"],
            ["Agama", "Salat Tahajud", "Kali"],
            ["Agama", "Baca Qur'an", "Juz"],
            ["Agama", "Zikir Pagi Petang", "Kali"],
            ["Kesehatan", "Jogging", "Menit"],
            ["Kesehatan", "Push Up", "Reps"],
            ["Kesehatan", "Squat Jump", "Reps"],
            ["Dompet", "Saldo Cash", "Rp"],
            ["Dompet", "Saldo Bank", "Rp"],
            ["Dompet", "Saldo E-Wallet (DANA + GoPay)", "Rp"],
            ["Dompet", "Saldo Ajaib", "Rp"],
            ["Investasi", "Aset Saham", "Rp"],
            ["Investasi", "Aset Reksadana", "Rp"],
            ["Investasi", "Aset Forex", "Rp"],
            ["Investasi", "Aset Kripto", "Rp"]
        ]
        ws_custom.append_rows(default_metrics)
        df_custom = load_data(ws_custom)

    kategori_list = sorted(df_custom["Kategori"].unique().tolist()) if "Kategori" in df_custom.columns else []
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = None

    st.markdown("#### Langkah 1: Pilih Kategori")
    cols = st.columns(len(kategori_list))
    for i, kat in enumerate(kategori_list):
        with cols[i]:
            if st.button(f"📂 {kat}", use_container_width=True):
                st.session_state.selected_category = kat
                st.rerun()

    if st.session_state.selected_category:
        st.markdown(f"#### ✏️ Langkah 2: Isi Data — {st.session_state.selected_category}")
        metrics = df_custom[df_custom["Kategori"] == st.session_state.selected_category]
        with st.form(f"form_{st.session_state.selected_category}", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1: bulan = st.selectbox("📅 Pilih Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"], index=8)
            with c2: minggu = st.selectbox("📆 Pilih Minggu", ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"])
            st.divider()
            input_rows = []
            for _, row in metrics.iterrows():
                metrik_nama = row["Nama Metrik"]
                satuan = row["Satuan"]
                c_val, c_note = st.columns([1, 1.5])
                with c_val:
                    step = 50000 if str(satuan).strip() == "Rp" else 1
                    nilai = st.number_input(f"{metrik_nama} ({satuan})", min_value=0, step=step, key=f"inp_{metrik_nama}")
                with c_note:
                    catatan = st.text_input(f"Catatan", key=f"note_{metrik_nama}", placeholder="Opsional...")
                input_rows.append([bulan, minggu, st.session_state.selected_category, metrik_nama, int(nilai), str(satuan), catatan.strip()])
            c_submit, c_clear = st.columns([2, 1])
            with c_submit: simpan = st.form_submit_button("✅ SIMPAN DATA", type="primary", use_container_width=True)
            with c_clear: 
                if st.form_submit_button("❌ Ganti Kategori", use_container_width=True):
                    st.session_state.selected_category = None
                    st.rerun()
            if simpan:
                with st.spinner("Menyimpan ke Google Sheets..."):
                    ws_log.append_rows(input_rows)
                    st.success(f"✅ Berhasil disimpan! Semangat terus, Dede! 💪✨")
                    st.session_state.selected_category = None
                    st.rerun()
    else:
        st.info("👆 Klik salah satu kategori di atas untuk mulai mencatat.")

# ---------------------------------------------------------
# 3. CATAT PENGELOUARAN
# ---------------------------------------------------------
elif menu == "💸 Catat Pengeluaran":
    st.markdown('<h2 class="gradient-header">💸 CATAT PENGELOUARAN HARIAN</h2>', unsafe_allow_html=True)
    st.write("Pilih dari dompet mana uangnya dipakai, otomatis terpotong saldonya.")
    with st.form("form_transaksi", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: bulan_t = st.selectbox("📅 Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"], index=8)
        with c2: minggu_t = st.selectbox("📆 Minggu", ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"])
        sumber_dana = st.selectbox("💰 Ambil Dari:", ["Cash", "Bank", "E-Wallet (DANA + GoPay)", "Ajaib"])
        nominal = st.number_input("💵 Nominal Pengeluaran (Rp):", min_value=0, step=10000, value=0)
        keperluan = st.text_input("📝 Keterangan Keperluan:", placeholder="Contoh: Beli buku, bayar listrik, makan...")
        btn_transaksi = st.form_submit_button("💸 SIMPAN & POTONG SALDO", type="primary", use_container_width=True)
    if btn_transaksi:
        if nominal > 0:
            with st.spinner("Menyimpan transaksi..."):
                metrik_name = f"Pengeluaran dari {sumber_dana}"
                ws_log.append_row([bulan_t, minggu_t, "Dompet", metrik_name, int(nominal), "Rp", keperluan or "-"])
                st.success(f"✅ Berhasil dicatat! Rp {nominal:,.0f} dipotong dari **{sumber_dana}** bulan {bulan_t}.")
                st.info("ℹ️ Investasi tidak tersentuh saat pengeluaran — hanya dompet yang berkurang.")
        else:
            st.warning("⚠️ Masukkan nominal yang lebih dari 0.")

# ---------------------------------------------------------
# 4. FOTO & REFLEKSI BULANAN
# ---------------------------------------------------------
elif menu == "🎯 Foto & Refleksi Bulanan":
    st.markdown('<h2 class="gradient-header">🎯 FOTO & REFLEKSI BULANAN</h2>', unsafe_allow_html=True)
    st.write("Simpan momen terbaik dan tuliskan pelajaran berharga bulan ini.")
    with st.form("form_bulanan", clear_on_submit=True):
        bulan_eval = st.selectbox("📅 Pilih Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"], index=8)
        foto_url_input = st.text_area("📸 Link Foto Bulan Ini (pisahkan dengan koma):", 
            placeholder="Contoh: https://i.ibb.co/xxx/foto1.jpg, https://i.ibb.co/xxx/foto2.jpg")
        evaluasi_umum = st.text_area("✍️ Refleksi & Catatan Bulan Ini:", height=150,
            placeholder="Apa pencapaian terbesarmu bulan ini? Apa yang perlu diperbaiki bulan depan? Apa yang kamu syukuri?")
        submit_bulanan = st.form_submit_button("🚀 SIMPAN JURNAL BULANAN", type="primary", use_container_width=True)
    if submit_bulanan:
        with st.spinner("Menyimpan ke Google Sheets..."):
            foto_clean = ", ".join([f.strip() for f in foto_url_input.split(",") if f.strip()])
            ws_bulanan.append_row([bulan_eval, "", "", "", "", evaluasi_umum.strip(), foto_clean])
            st.success(f"🎉 Selesai! Refleksi & foto bulan {bulan_eval} tersimpan dengan baik. Terima kasih sudah berjalan sejauh ini, Dede! 🙌✨")

# ---------------------------------------------------------
# 5. KELOLA KATEGORI & METRIK
# ---------------------------------------------------------
elif menu == "⚙️ Kelola Kategori & Metrik":
    st.markdown('<h2 class="gradient-header">⚙️ KELOLA KATEGORI & METRIK</h2>', unsafe_allow_html=True)
    st.write("Tambah, lihat, atau hapus metrik pencatatanmu.")
    df_custom = load_data(ws_custom)
    tab1, tab2 = st.tabs(["➕ Tambah Baru", "📋 Daftar Metrik"])
    with tab1:
        with st.form("form_tambah_metrik", clear_on_submit=True):
            kat_baru = st.text_input("📂 Nama Kategori", placeholder="Misal: Hobi, Side Project, Belajar Pemrograman...")
            metrik_baru = st.text_input("📝 Nama Metrik / Kegiatan", placeholder="Misal: Jam Belajar, Proyek Selesai, Bab Dibaca...")
            satuan_baru = st.text_input("📏 Satuan Pengukuran", placeholder="Misal: Jam, Halaman, Proyek, Kali, Rp...")
            submit_custom = st.form_submit_button("➕ TAMBAH METRIK", type="primary", use_container_width=True)
        if submit_custom:
            if kat_baru.strip() and metrik_baru.strip() and satuan_baru.strip():
                ws_custom.append_row([kat_baru.strip(), metrik_baru.strip(), satuan_baru.strip()])
                st.success(f"✅ Metrik **'{metrik_baru}'** di bawah kategori **'{kat_baru}'** berhasil ditambahkan!")
                st.rerun()
            else:
                st.warning("⚠️ Lengkapi semua kolom sebelum menambah.")
    with tab2:
        st.dataframe(df_custom, use_container_width=True, hide_index=True)
        st.divider()
        st.info("💡 Untuk mengedit atau menghapus metrik, silakan langsung edit di Google Sheet 'Category_Custom'. Perubahan akan otomatis terlihat di web ini.")
        st.markdown("[🔗 Buka Google Sheet](https://docs.google.com/spreadsheets/d/17-zwnUwDzk9jxx1_jnFyqJ2SSC1xHT5nZ6dZdHgfGvA/edit)")
