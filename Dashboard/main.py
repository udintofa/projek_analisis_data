import numpy as np
import matplotlib.pyplot as plt
import os as os
import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

order_item = pd.read_csv(r'Data/order_items_dataset.csv') #order, produk, seller
order = pd.read_csv(r'Data/orders_dataset.csv') #order, customer, status
seller = pd.read_csv(r'Data/sellers_dataset.csv') #seller, city
customer = pd.read_csv(r'Data/customers_dataset.csv') #customer, city
product = pd.read_csv(r'Data/products_dataset.csv') #product_id, category_product
geolocation = pd.read_csv(r'Data/geolocation_dataset.csv')

order.order_delivered_customer_date.fillna(order.order_estimated_delivery_date, inplace=True)
order.order_approved_at.fillna(order.order_purchase_timestamp, inplace=True)
order.order_delivered_carrier_date.fillna(order.order_approved_at, inplace=True)
datetime_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
for column in datetime_columns:
  order[column] = pd.to_datetime(order[column])
product.dropna(inplace=True)
geolocation.drop_duplicates(inplace=True)


st.title("Projek Analisis Data Dicoding")
st.write("""
Nama : Muchammad Udin Mustofa\n
Email: muchammad.udin.mustofa@mail.ugm.ac.id\n
ID   : udintofa
""")
st.header("E-Commerce Public Dataset by Olist")
st.subheader("Exploratory Data Analisys")

with st.expander("Explore order"):
    st.write('Sampel')
    st.dataframe(order.sample(5))
    st.write("Deskripsi Data")
    st.dataframe(order.describe(include="all"))

with st.expander("Explore order_item"):
    st.write("Sampel")
    st.dataframe(order_item.sample(5))
    st.write("Deskripsi Data")
    st.dataframe(order_item.describe(include='all'))
    st.write("Jumlah produk yg dibeli dalam sekali pembelian")
    st.dataframe(order_item.groupby(by="order_id").order_item_id.sum().sort_values(ascending=False))
    st.write("Produk paling laku")
    produk_paling_laku = order_item.groupby(by="product_id").order_item_id.sum().sort_values(ascending=False)
    produk_paling_laku = produk_paling_laku.reset_index()
    st.dataframe(produk_paling_laku.head())
    st.write("Penjual paling laku")
    penjual_paling_laku = order_item.groupby(by="seller_id").order_item_id.sum().sort_values(ascending=False)
    penjual_paling_laku = penjual_paling_laku.reset_index()
    st.dataframe(penjual_paling_laku.head())

with st.expander("Explore order dan order_item"):
    order_seller_customer = pd.merge(
    left=order,
    right=order_item,
    how='inner',
    left_on='order_id',
    right_on='order_id'
    )
    st.write("Sampel Merger dari order dan orer_item")
    st.dataframe(order_seller_customer.sample(5))
    st.write("Deskripsi data")
    st.dataframe(order_seller_customer.describe(include='all'))

with st.expander("Explore seller"):
    st.write("Sampel")
    st.dataframe(seller.sample(5))
    st.write("Deskripsi")
    st.dataframe(seller.describe(include='all'))
    st.write('Jumlah seller tiap kota')
    st.dataframe(seller.groupby(by="seller_city").seller_id.nunique().sort_values(ascending=False))
    st.write('Jumlah seller tiap state')
    st.dataframe(seller.groupby(by="seller_state").seller_id.nunique().sort_values(ascending=False))

with st.expander("Explore customer"):
    st.write("Sample")
    st.dataframe(customer.sample(5))
    st.write("Deskripsi data")
    st.dataframe(customer.describe(include='all'))
    st.write('Jumlah customer tiap kota')
    st.dataframe(customer.groupby(by="customer_city").customer_id.nunique().sort_values(ascending=False))
    st.write('Jumlah customer tiap state')
    st.dataframe(customer.groupby(by="customer_state").customer_id.nunique().sort_values(ascending=False))

with st.expander("Explore order & order_item & seller & customer"):
    order_seller_customer_kota_seller = pd.merge(
    left=order_seller_customer,
    right=seller,
    how='inner',
    left_on='seller_id',
    right_on='seller_id'
    )
    order_kota = pd.merge(
    left=order_seller_customer_kota_seller,
    right=customer,
    how='inner',
    left_on='customer_id',
    right_on='customer_id'
    )
    order_kota.drop(columns=[
    'order_status',
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_customer_date',
    'order_delivered_carrier_date',
    'order_estimated_delivery_date',
    'order_item_id',
    'shipping_limit_date',
    'price',
    'freight_value',
    'customer_unique_id',
    ])
    st.write("Sampel")
    st.dataframe(order_kota.sample(5))
    st.write("Deskripsi Data")
    st.dataframe(order_kota.describe(include='all'))
    kota_paling_laku = order_kota.groupby(by='seller_city').order_id.nunique().sort_values(ascending=False)
    kota_paling_laku = kota_paling_laku.reset_index()
    kota_konsumtif = order_kota.groupby(by='customer_city').order_id.nunique().sort_values(ascending=False)
    kota_konsumtif = kota_konsumtif.reset_index()
    st.write("Kota paling laku")
    st.dataframe(kota_paling_laku.head(5))
    st.write("Kota paling konsumtif")
    st.dataframe(kota_konsumtif.head(5))

with st.expander("Explore product"):
    st.write("Sampel")
    st.dataframe(product.sample(5))
    st.write("Deskripsi data")
    st.dataframe(product.describe(include='all'))
    st.write("Banyak jenis produk yg dijual")
    st.dataframe(product.groupby(by="product_category_name").product_id.nunique().sort_values(ascending=False))
    st.write("Produk paling laku")
    nama_produk = pd.merge(
    left=produk_paling_laku,
    right=product,
    how='inner',
    left_on='product_id',
    right_on='product_id'
    )
    nama_produk = nama_produk[['product_id', 'product_category_name', 'order_item_id']]
    st.dataframe(nama_produk.head(10))

with st.expander("Explore geolocation"):
    st.write("Sample")
    st.dataframe(geolocation.sample(5))
    st.write("Deskripsi data")
    st.dataframe(geolocation.describe(include='all'))
    st.write("Lokasi Penjual Paling laku")
    lokasi_penjual = pd.merge(
    left=seller,
    right=geolocation,
    how='inner',
    left_on='seller_zip_code_prefix',
    right_on='geolocation_zip_code_prefix'
    )
    lokasi_penjual_paling_laku = pd.merge(
    left=penjual_paling_laku,
    right=lokasi_penjual,
    how='inner',
    left_on='seller_id',
    right_on='seller_id'
    )
    lokasi_penjual_paling_laku = lokasi_penjual_paling_laku.groupby(by='seller_id').agg({
    'order_item_id': 'count',
    'geolocation_lat': 'first',
    'geolocation_lng': 'first'
    }).sort_values(by='order_item_id', ascending=False)
    lokasi_penjual_paling_laku = lokasi_penjual_paling_laku.reset_index()
    st.dataframe(lokasi_penjual_paling_laku.head(10))

st.subheader("Visualization & Explanatory Analysis")
with st.expander("Pertanyaan 1: Dimana lokasi geografis tingkat penjualan tertinggi serta lokasi geografis tingkat pembelian produk tertinggi?"):
    st.write("Lokasi geografis tingkat penjualan tertinggi")
    st.dataframe(kota_paling_laku.head(10))

    st.write("Visualisasi")
    top_10_paling_laku = kota_paling_laku.head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(top_10_paling_laku['seller_city'], top_10_paling_laku['order_id'])
    ax.set_xticks(range(len(top_10_paling_laku['seller_city'])))
    ax.set_xticklabels(top_10_paling_laku['seller_city'], rotation=60)
    ax.set_title('Kota dengan Penjualan Tertinggi')
    ax.set_xlabel('Kota')
    ax.set_ylabel('Jumlah Penjualan')
    st.pyplot(fig)

    st.write("Lokasi geografis tingkat pembelian tertinggi")
    st.dataframe(kota_konsumtif.head(10))
    st.write("Visualisasi")
    top_10_konsumtif = kota_konsumtif.head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(top_10_konsumtif['customer_city'], top_10_konsumtif['order_id'])
    ax.set_xticks(range(len(top_10_konsumtif['customer_city'])))
    ax.set_xticklabels(top_10_konsumtif['customer_city'], rotation=60)
    ax.set_title('Kota dengan Pembelian Tertinggi')
    ax.set_xlabel('Kota')
    ax.set_ylabel('Jumlah Pembelian')
    st.pyplot(fig)

with st.expander("Pertanyaan 2: Produk manakah yang paling banyak terjual pada periode $2016-2018$?"):
    st.write('Produk yang paling banyak terjual')
    produk_paling_laku = nama_produk.groupby(by='product_category_name').order_item_id.sum().sort_values(ascending=False)
    produk_paling_laku = produk_paling_laku.reset_index()
    st.dataframe(produk_paling_laku.head(10))

    st.write("Visualisasi")
    top_10_produk = produk_paling_laku.head(10)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(top_10_produk['product_category_name'], top_10_produk['order_item_id'])
    ax.set_xticks(range(len(top_10_produk['product_category_name'])))
    ax.set_xticklabels(top_10_produk['product_category_name'], rotation=60)
    ax.set_title('Produk paling banyak terjual')
    ax.set_xlabel('Produk')
    ax.set_ylabel('Jumlah Penjualan')
    st.pyplot(fig)

st.subheader("Analisis Lanjutan")
with st.expander("Lokasi penjual paling laku"):
    top_10_penjual = lokasi_penjual_paling_laku.head(10)
    peta = folium.Map(location=[-21.55052, -46.633308], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(peta)
    for index, seller in top_10_penjual.iterrows():
        folium.Marker(
            location=[seller['geolocation_lat'], seller['geolocation_lng']],
            popup=f"Seller ID: {seller['seller_id']}",
            icon=folium.Icon(color="blue")
        ).add_to(marker_cluster)
    st_data = st_folium(peta, width=700, height=500)

st.subheader("Conclusion Pertanyaan")
with st.expander("Pertanyaan 1"):
    st.write("Dimana lokasi geografis tingkat penjualan tertinggi serta lokasi geografis tingkat pembelian produk tertinggi?")
    st.write("Lokasi geografis tingkat penjualan tertinggi")
    st.dataframe(kota_paling_laku.head(10))

    st.write("Visualisasi")
    top_10_paling_laku = kota_paling_laku.head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(top_10_paling_laku['seller_city'], top_10_paling_laku['order_id'])
    ax.set_xticks(range(len(top_10_paling_laku['seller_city'])))
    ax.set_xticklabels(top_10_paling_laku['seller_city'], rotation=60)
    ax.set_title('Kota dengan Penjualan Tertinggi')
    ax.set_xlabel('Kota')
    ax.set_ylabel('Jumlah Penjualan')
    st.pyplot(fig)

    st.write("Lokasi geografis tingkat pembelian tertinggi")
    st.dataframe(kota_konsumtif.head(10))
    st.write("Visualisasi")
    top_10_konsumtif = kota_konsumtif.head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(top_10_konsumtif['customer_city'], top_10_konsumtif['order_id'])
    ax.set_xticks(range(len(top_10_konsumtif['customer_city'])))
    ax.set_xticklabels(top_10_konsumtif['customer_city'], rotation=60)
    ax.set_title('Kota dengan Pembelian Tertinggi')
    ax.set_xlabel('Kota')
    ax.set_ylabel('Jumlah Pembelian')
    st.pyplot(fig)

    with st.container():
        st.markdown('''
        Terdapat urutan kota dari jumlah penjualan paling tinggi, kita ambil 10 kota dengan penjualan tertinggi.  
        Diperoleh Urutan kota dengan jumlah penjualan paling tinggi adalah **Sao Paulo, Ibitinga, Curitiba, Santo Andre, 
        Belo Horizonte, Rio de Janeiro, Guarulhos, Ribeirao Preto, Sao Jose do Rio Preto, dan Maringa**.  

        Terdapat urutan kota dari jumlah pembelian paling tinggi, kita ambil 5 kota dengan pembelian tertinggi.  
        Diperoleh urutan kota dengan jumlah pembelian paling tinggi adalah **Sao Paulo, Rio de Janeiro, Belo Horizonte, 
        Brasilia, Curitiba, Campinas, Porto Alegre, Salvador, Guarulhos, dan Sao Bernardo do Campo**.  

        Dengan jumlah pembelian pada periode tersebut tertera pada tabel di atas. Kedua hasil analisis data di atas 
        akan memberikan informasi yang sangat penting bagi perusahaan jasa kirim. Mereka mendapatkan informasi lebih 
        mengenai dari kota mana yang paling banyak mengirim barang dan dari kota mana yang menjadi tujuan pengiriman 
        barang tersebut.
        ''')

with st.expander("Pertanyaan 2"):
    st.write("Produk manakah yang paling banyak terjual pada periode $2016-2018$?")
    st.write('Produk yang paling banyak terjual')
    produk_paling_laku = nama_produk.groupby(by='product_category_name').order_item_id.sum().sort_values(ascending=False)
    produk_paling_laku = produk_paling_laku.reset_index()
    st.dataframe(produk_paling_laku.head(10))

    st.write("Visualisasi")
    top_10_produk = produk_paling_laku.head(10)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(top_10_produk['product_category_name'], top_10_produk['order_item_id'])
    ax.set_xticks(range(len(top_10_produk['product_category_name'])))
    ax.set_xticklabels(top_10_produk['product_category_name'], rotation=60)
    ax.set_title('Produk paling banyak terjual')
    ax.set_xlabel('Produk')
    ax.set_ylabel('Jumlah Penjualan')
    st.pyplot(fig)

    with st.container():
        st.markdown('''
        Terdapat urutan nama produk dari jumlah order paling tinggi, kita ambil 10 nama produk dengan order tertinggi. 
        Diperoleh urutan produk dengan jumlah order paling tinggi adalah Cama Mesa Banho (Tempat tidur, meja dan kamar mandi) dengan jumlah $10952$ order. 
        Dengan jumlah order pada periode tersebut tertera pada tabel diatas. 
        Data tersebut akan berguna bagi para seller dalam meningkatkan produksi barang yang paling diminati oleh masyarakat.
        ''')
