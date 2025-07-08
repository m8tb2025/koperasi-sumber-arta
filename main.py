import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# -------------------------------
# Load dan perbaiki data
# -------------------------------
try:
    kas_df = pd.read_csv("kas.csv", on_bad_lines='skip', encoding='utf-8')
except Exception as e:
    st.error(f"❌ Gagal memuat data kas.csv: {e}")
    st.stop()

kas_df["Tanggal"] = pd.to_datetime(kas_df["Tanggal"], errors="coerce")

try:
    anggota_df = pd.read_csv("anggota.csv")
    simpan_pinjam_df = pd.read_csv("simpan_pinjam.csv")
    jurnal_df = pd.read_csv("jurnal.csv")
except:
    anggota_df = pd.DataFrame()
    simpan_pinjam_df = pd.DataFrame()
    jurnal_df = pd.DataFrame()

# -------------------------------
# Sidebar menu
# -------------------------------
st.sidebar.title("Koperasi Sumber Arta Wanita")
menu = st.sidebar.selectbox("Pilih Menu", ["Dashboard", "Buku Kas", "Data Anggota", "Simpan Pinjam", "Jurnal Umum"])

# -------------------------------
# Dashboard
# -------------------------------
if menu == "Dashboard":
    st.title("📊 Dashboard Koperasi")

    pemasukan = kas_df[kas_df['Kategori'] == 'Pemasukan']['Jumlah (Rp)'].sum()
    pengeluaran = kas_df[kas_df['Kategori'] == 'Pengeluaran']['Jumlah (Rp)'].sum()
    saldo = pemasukan - pengeluaran

    st.metric("Total Pemasukan", f"Rp {pemasukan:,.0f}")
    st.metric("Total Pengeluaran", f"Rp {pengeluaran:,.0f}")
    st.metric("Saldo Akhir", f"Rp {saldo:,.0f}")

    st.subheader("Grafik Arus Kas Bulanan")
    kas_df['Bulan'] = kas_df['Tanggal'].dt.to_period('M')
    monthly = kas_df.groupby(['Bulan', 'Kategori'])['Jumlah (Rp)'].sum().unstack().fillna(0)

    fig, ax = plt.subplots()
    monthly.plot(kind='bar', stacked=True, ax=ax)
    plt.title("Pemasukan vs Pengeluaran")
    plt.xlabel("Bulan")
    plt.ylabel("Jumlah (Rp)")
    st.pyplot(fig)

# -------------------------------
# Buku Kas
# -------------------------------
elif menu == "Buku Kas":
    st.title("📒 Buku Kas")

    st.subheader("Data Transaksi")
    for i, row in kas_df.sort_values(by="Tanggal", ascending=False).reset_index().iterrows():
        col1, col2 = st.columns([6, 1])
        with col1:
            tgl_str = row['Tanggal'].date() if pd.notnull(row['Tanggal']) else "❓ Invalid Tanggal"
            st.write(f"📅 **{tgl_str}** | {row['Kategori']} | {row['Keterangan']} — Rp {row['Jumlah (Rp)']:,.0f}")
        with col2:
            if st.button("Edit", key=f"edit_{i}"):
                st.session_state.edit_index = i
            if st.button("❌", key=f"delete_{i}"):
                kas_df = kas_df.drop(index=row['index'])
                kas_df.to_csv("kas.csv", index=False)
                st.experimental_rerun()

    st.divider()

    edit_mode = "edit_index" in st.session_state
    st.subheader("✏️ Edit Transaksi" if edit_mode else "➕ Tambah Transaksi Baru")

    if edit_mode:
        row = kas_df.iloc[st.session_state.edit_index]
        default_tgl = row["Tanggal"] if pd.notnull(row["Tanggal"]) else datetime.today()
        default_ket = row["Keterangan"]
        default_kat = row["Kategori"]
        default_jml = row["Jumlah (Rp)"]
    else:
        default_tgl = datetime.today()
        default_ket = ""
        default_kat = "Pemasukan"
        default_jml = 0

    tgl = st.date_input("Tanggal", value=default_tgl)
    ket = st.text_input("Keterangan", value=default_ket)
    kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"], index=0 if default_kat == "Pemasukan" else 1)
    jumlah = st.number_input("Jumlah (Rp)", step=1000, value=int(default_jml))

    col_save, col_cancel = st.columns([1, 1])
    with col_save:
        if st.button("💾 Simpan"):
            new_data = pd.DataFrame({
                "Tanggal": [tgl],
                "Keterangan": [ket],
                "Kategori": [kategori],
                "Jumlah (Rp)": [jumlah]
            })
            if edit_mode:
                kas_df.iloc[st.session_state.edit_index] = new_data.iloc[0]
                del st.session_state.edit_index
            else:
                kas_df = pd.concat([kas_df, new_data], ignore_index=True)
            kas_df.to_csv("kas.csv", index=False)
            st.success("✅ Data berhasil disimpan!")
            st.experimental_rerun()

    with col_cancel:
        if edit_mode and st.button("Batal"):
            del st.session_state.edit_index
            st.experimental_rerun()

# -------------------------------
# Data Anggota
# -------------------------------
elif menu == "Data Anggota":
    st.title("👥 Data Anggota")
    if anggota_df.empty:
        st.info("Belum ada data anggota.")
    else:
        st.dataframe(anggota_df)

# -------------------------------
# Simpan Pinjam
# -------------------------------
elif menu == "Simpan Pinjam":
    st.title("💰 Buku Simpan Pinjam")
    if simpan_pinjam_df.empty:
        st.info("Belum ada data simpan pinjam.")
    else:
        st.dataframe(simpan_pinjam_df)

# -------------------------------
# Jurnal Umum
# -------------------------------
elif menu == "Jurnal Umum":
    st.title("📘 Jurnal Umum")
    if jurnal_df.empty:
        st.info("Belum ada data jurnal.")
    else:
        st.dataframe(jurnal_df)

# -------------------------------
# Footer
# -------------------------------
st.sidebar.caption("Made with ❤️ for Koperasi Sumber Arta Wanita")
