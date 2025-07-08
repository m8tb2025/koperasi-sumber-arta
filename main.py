import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Load data
kas_df = pd.read_csv("kas.csv")
anggota_df = pd.read_csv("anggota.csv")
simpan_pinjam_df = pd.read_csv("simpan_pinjam.csv")
jurnal_df = pd.read_csv("jurnal.csv")

# Format tanggal
kas_df['Tanggal'] = pd.to_datetime(kas_df['Tanggal'])

# Sidebar menu
st.sidebar.title("Koperasi Sumber Arta Wanita")
menu = st.sidebar.selectbox("Pilih Menu", ["Dashboard", "Buku Kas", "Data Anggota", "Simpan Pinjam", "Jurnal Umum"])

# Halaman Dashboard
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

elif menu == "Buku Kas":
    st.title("📒 Buku Kas")
    st.dataframe(kas_df.sort_values(by="Tanggal", ascending=False))

    with st.expander("Tambah Transaksi Baru"):
        tgl = st.date_input("Tanggal", value=datetime.today())
        ket = st.text_input("Keterangan")
        kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
        jumlah = st.number_input("Jumlah (Rp)", step=1000)

        if st.button("Simpan Transaksi"):
            new_data = pd.DataFrame({
                "Tanggal": [tgl.strftime('%Y-%m-%d')],
                "Keterangan": [ket],
                "Kategori": [kategori],
                "Jumlah (Rp)": [jumlah]
            })
            kas_df = pd.concat([kas_df, new_data], ignore_index=True)
            kas_df.to_csv("kas.csv", index=False)
            st.success("Transaksi berhasil disimpan!")
            st.experimental_rerun()

elif menu == "Data Anggota":
    st.title("👥 Data Anggota")
    st.dataframe(anggota_df)

elif menu == "Simpan Pinjam":
    st.title("💰 Buku Simpan Pinjam")
    st.dataframe(simpan_pinjam_df)

elif menu == "Jurnal Umum":
    st.title("📘 Jurnal Umum")
    st.dataframe(jurnal_df)

st.sidebar.caption("Made with ❤️ for Koperasi Sumber Arta Wanita")
