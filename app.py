import streamlit as st
import pandas as pd
import plotly.express as px

# (Bagian koneksi Google Sheets & sidebar sama seperti sebelumnya...)

# ---------------------------------------------------------
# HALAMAN DASHBOARD & RINGKASAN PROFIL
# ---------------------------------------------------------
if menu == "📊 Dashboard & Rekapitulasi":
    st.title("📌 Personal Progress Dashboard")
    
    # 1. URL Foto dari ImgBB (Bisa diubah fleksibel lewat sidebar atau input)
    # Masukkan direct link foto ImgBB kamu di sini
    default_foto_url = "https://i.ibb.co/sample-image.jpg" 
    
    with st.sidebar.expander("🖼️ Pengaturan Foto Profil"):
        foto_url = st.text_input("Link Foto ImgBB (Direct Link):", value=default_foto_url)

    df_log = load_data(ws_log)
    df_b = load_data(ws_bulanan)
    
    # Pilih Bulan yang mau ditinjau
    bulan_list = df_log["Bulan"].unique() if not df_log.empty else ["September"]
    bulan_selected = st.selectbox("🗓️ Pilih Bulan Tinjauan:", bulan_list)

    st.divider()

    # ---------------------------------------------------------
    # HERO SECTION (FOTO PROFIL + INTRO BULANAN)
    # ---------------------------------------------------------
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
            "Berikut adalah akumulasi dari seluruh komitmen harian dan mingguan dalam aspek "
            "**Pengetahuan, Agama, Kesehatan, dan Keuangan**."
        )
        
        # Ambil catatan evaluasi umum jika ada
        evaluasi_text = "Belum ada catatan evaluasi untuk bulan ini."
        if not df_b.empty and "Bulan" in df_b.columns:
            df_b_filter = df_b[df_b["Bulan"] == bulan_selected]
            if not df_b_filter.empty:
                evaluasi_text = df_b_filter.iloc[-1].get('Evaluasi Umum & Catatan', evaluasi_text)

        st.info(f"💡 **Catatan / Evaluasi Bulan Ini:**\n\n_{evaluasi_text}_")

    st.divider()

    # ---------------------------------------------------------
    # HIGHLIGHT METRICS BULANAN (ANGKA KUNCI)
    # ---------------------------------------------------------
    st.markdown("### 🎯 Angka Kunci Pencapaian Bulan Ini")
    
    if not df_log.empty:
        df_filtered = df_log[df_log["Bulan"] == bulan_selected]
        
        # Kalkulasi Angka
        df_agg = df_filtered.groupby(["Kategori", "Metrik / Nama Kegiatan"])["Nilai"].sum().reset_index()
        
        m1, m2, m3, m4 = st.columns(4)
        
        # Contoh ekstraksi metrik utama
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

        # ---------------------------------------------------------
        # RINGKASAN DETAIL KATEGORI (KARTU KATEGORI)
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # GRAFIK VISUALISASI
        # ---------------------------------------------------------
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
        st.info("Belum ada data log mingguan yang diinput.")
