import numpy as np
import matplotlib.pyplot as plt
import os as os
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import contextily as cx
import geopandas as gpd

order_item = pd.read_csv(r'Data/order_items_dataset.csv') #order, produk, seller
order = pd.read_csv(r'Data/orders_dataset.csv') #order, customer, status
seller = pd.read_csv(r'Data/sellers_dataset.csv') #seller, city
customer = pd.read_csv(r'Data/customers_dataset.csv') #customer, city
product = pd.read_csv(r'Data/products_dataset.csv') #product_id, category_product
geolocation = pd.read_csv(r'Data/geolocation_dataset.csv')

order.dropna(inplace=True)
product.dropna(inplace=True)

order_fix = pd.merge(
    left=order,
    right=order_item,
    how='inner',
    left_on='order_id',
    right_on='order_id'
)
order_kota_customer = pd.merge(
    left=order_fix,
    right=customer,
    how='inner',
    left_on='customer_id',
    right_on='customer_id'
)
order_kota = pd.merge(
    left=order_kota_customer,
    right=seller,
    how='inner',
    left_on='seller_id',
    right_on='seller_id'
)
kota_pembeli = order_kota.groupby(by='customer_city').agg({
    'order_id': 'count'
    }).sort_values(by='order_id', ascending=False).head(5)

kota_penjual = order_kota.groupby(by='seller_city').agg({
    'order_id': 'count'
    }).sort_values(by='order_id', ascending=False).head(5)

top_produk = order_kota.groupby(by='product_id').agg({
     'order_id': 'count'
     }).sort_values(by='order_id', ascending=False)

nama_produk = pd.merge(
    left=top_produk,
    right=product,
    how='inner',
    left_on='product_id',
    right_on='product_id'
)
nama_produk = nama_produk[["product_id", "product_category_name", "order_id"]]

jumlah_produk = nama_produk.groupby(by='product_category_name').agg({
    'order_id': 'sum'
    }).sort_values(by='order_id', ascending=False).head(10)



sao_paulo = order_kota[order_kota['seller_city']=='sao paulo']

top_sao_paulo = sao_paulo.groupby(by='seller_id').agg({
    'order_id': 'count',
    'seller_zip_code_prefix': 'first'
    }).sort_values(by='order_id', ascending=False)

top_sao_paulo_geolocation = pd.merge(
    left=top_sao_paulo,
    right=geolocation,
    how='inner',
    left_on='seller_zip_code_prefix',
    right_on='geolocation_zip_code_prefix'
).sort_values(by='order_id', ascending=False)

top_5_seller_sao_paulo = top_sao_paulo_geolocation.groupby(by='order_id').agg({
    'seller_zip_code_prefix': 'first',
    'geolocation_lat': 'first',
    'geolocation_lng': 'first'
    }).sort_values(by='order_id', ascending=False).head(10)
top_5_seller_sao_paulo.reset_index(inplace=True)

import folium
from IPython.display import display



##########Ini memulai untuk menampilkan di web yang dibuat###################
st.title("Projek Analisis Data")
st.subheader("E-Commerce Public Dataset")
st.markdown(
    '''
    Nama: Muchammad Udin Mustofa\n
    Email: muchammad.udin.mustofa@mail.ugm.ac.id\n
    ID Dicoding: udintofa
    '''
)
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Pertanyaan 1", "Pertanyaan 2", "Analisis Lanjutan"])

with tab1:
    st.header("Tentang Projek Analisis Data")
    st.markdown(
        """
        Ini adalah projek dalam modul Belajar Analisis Data dengan Python. Dataset yang diambil adalah E-Commerce Public Dataset.
        Dalam menganalisis data, diambil 2 buah pertanyaan, yaitu:\n
        1. Dimana lokasi geografis dengan tingkat pembelian serta lokasi geografis penjualan produk tertinggi?\n
        2. Produk manakah yang memiliki jumlah order paling banyak pada periode tersebut?
        """
    )

with tab2:
    st.title("Pertanyaan 1")
    st.write("Dimana lokasi geografis dengan tingkat pembelian serta lokasi geografis penjualan produk tertinggi?")
    
    st.header("Lokasi dg Penjualan Tertinggi")
    # Dataframe kota_penjual
    st.dataframe(kota_penjual)
    st.write("Terdapat urutan kota dari jumlah penjualan paling tinggi, kita ambil 5 kota dengan penjualan tertiinggi. Diperoleh Urutan kota dengan jumlah penjualan paling tinggi adalah Sao paulo, Ibitinga, Curitiba, Santo Andre, dan Sao Jose di Rio Preto. Dengan jumlah penjualan pada periode tersebut tertera pada tabel diatas.")
    # Plot grafik bar untuk kota penjual
    fig, ax = plt.subplots()
    ax.bar(x=kota_penjual.index, height=kota_penjual['order_id'])
    plt.xticks(rotation=60)
    st.pyplot(fig)
    st.write("Jika divisualisasikan dengan dengan bar chart, diperoleh visualisasi seperti grafik diatas. Kota dengan penjualan paling banyak adalah Sao Paulo dengan jumlah penjualannya adalah $27350$ transaksi pada periode tersebut. Dikuti dengan 4 kota lainnya yang berbanding jauh lebih sedikit daripada kota Sao Paulo.")

    st.header("Lokasi dg PembelianTertinggi")
    # Dataframe kota_pembeli
    st.dataframe(kota_pembeli)
    st.write("Terdapat urutan kota dari jumlah pembelian paling tinggi, kita ambil 5 kota dengan pembelian tertinggi. Diperoleh urutan kota dengan jumlah pembelian paling tinggi adalah Sao paulo, Rio de Janeiro, Belo Horizonte, Brasilia, dan Curitiba. Dengan jumlah pembelian pada periode tersebut tertera pada tabel diatas.")
    # Plot grafik bar untuk kota pembeli
    fig, ax = plt.subplots()
    ax.bar(x=kota_pembeli.index, height=kota_pembeli['order_id'])
    plt.xticks(rotation=60)
    st.pyplot(fig)
    st.write("Jika divisualisasikan dengan dengan bar chart, diperoleh visualisasi seperti grafik diatas. Kota dengan pembelian paling banyak adalah Sao Paulo dengan jumlah pembeliannya adalah $17400$ transaksi pada periode tersebut. Dikuti dengan 4 kota lainnya yang berbanding cukup lebih sedikit daripada kota Sao Paulo.")

with tab3:
    st.header("Pertanyaan 2")
    st.write("Produk manakah yang memiliki jumlah order paling banyak pada periode tersebut?")
    st.dataframe(jumlah_produk)
    st.write("Terdapat urutan nama produk dari jumlah order paling tinggi, kita ambil 10 nama produk dengan order tertinggi. Diperoleh urutan produk dengan jumlah order paling tinggi adalah Cama Mesa Banho (Tempat tidur, meja dan kamar mandi) dengan jumlah $10952$ order. Dengan jumlah order pada periode tersebut tertera pada tabel diatas.")
    fig, ax = plt.subplots()
    ax.bar(x=jumlah_produk.index, height=jumlah_produk['order_id'])
    plt.xticks(rotation=60)
    st.title("Jumlah Order per Kota Penjual")
    st.pyplot(fig)
    st.write("Jika divisualisasikan dengan dengan bar chart, diperoleh visualisasi seperti grafik diatas. Nama produk dengan order paling banyak adalah Cama Mesa Banho (Tempat tidur, meja dan kamar mandi) dengan jumlah $10952$ order pada periode tersebut. Dikuti dengan 9 produk lainnya yang jumlah ordernya ada dibawah Cama Mesa Banho.")

with tab4:
    st.title("Analisis Lanjutan Menggunakan Folium dan Geopandas")
    st.write("Dibuat sebuah analisis lanjutan untuk mengetahui lokasi 5 penjual dengan jumlah order terbanyak pada periode 2016-2018 di kota Sao Paulo.")
    # Membuat peta dengan folium
    # peta = folium.Map(location=[-23.55052, -46.633308], zoom_start=12)

    # # Menambahkan marker dari data top 5 seller
    # for index, seller in top_5_seller_sao_paulo.iterrows():
    #     folium.Marker(
    #         location=[seller['geolocation_lat'], seller['geolocation_lng']],
    #         popup=f"Order ID: {seller['order_id']}\nZip Code: {seller['seller_zip_code_prefix']}",
    #         icon=folium.Icon(color="blue")
    #     ).add_to(peta)

    # # Tampilkan peta menggunakan streamlit-folium dengan ukuran lebih besar
    # st.title("Peta dengan Folium")
    # st_folium(peta, width=700, height=500)
    # peta = folium.Map(location=[-23.55052, -46.633308], zoom_start=12)

    # # Menambahkan marker dari data top 5 seller
    # for index, seller in top_5_seller_sao_paulo.iterrows():
    #     folium.Marker(
    #         location=[seller['geolocation_lat'], seller['geolocation_lng']],
    #         popup=f"Order ID: {seller['order_id']}\nZip Code: {seller['seller_zip_code_prefix']}",
    #         icon=folium.Icon(color="blue")
    #     ).add_to(peta)

    # # Tampilkan peta menggunakan streamlit-folium dengan ukuran lebih besar
    # st.title("Peta dengan Folium")
    # st_folium(peta, width=700, height=500)

    df = gpd.GeoDataFrame(top_5_seller_sao_paulo, geometry=gpd.points_from_xy(top_5_seller_sao_paulo['geolocation_lng'], top_5_seller_sao_paulo['geolocation_lat']))
    
    # Set CRS ke EPSG:4326 (koordinat latitude/longitude WGS 84)
    df.set_crs(epsg=4326, inplace=True)
    
    # Plot GeoDataFrame
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot(ax=ax, color='blue', marker='o', markersize=50, label="Penjual")

    # Tambahkan peta dasar menggunakan contextily
    cx.add_basemap(ax, crs=df.crs, source=cx.providers.OpenStreetMap.Mapnik)

    ax.set_title("Peta Penjual di Sao Paulo")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    
    st.pyplot(fig)
