import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-commerce Analytics")
st.title("📊 E-commerce Analytics Dashboard")

# dataframes
events_df = pd.read_csv("data/events.csv")
product_df = pd.read_csv("data/producto.csv")
category_df = pd.read_csv("data/categoria.csv")
brand_df = pd.read_csv("data/marca.csv")
client_df = pd.read_csv("data/cliente.csv", encoding='mac_roman')
event_df = pd.read_csv("data/events.csv")

compras = events_df[events_df['event'] == 'transaction']


def event_counts(events_df):
    # Contar eventos por tipo
    event_counts = events_df['event'].value_counts()

    fig, ax = plt.subplots()
    sns.barplot(x=event_counts.index, y=event_counts.values, palette='pastel', ax=ax)
    ax.set_ylabel("Cantidad de eventos")
    ax.set_xlabel("Tipo de evento")
    ax.set_title("Distribución de eventos")
    st.pyplot(fig)


def plot_top_clients_streamlit(events_df, client_df, top_n=10):
    """
    Muestra en Streamlit un gráfico de barras con los clientes que tienen más compras.

    Args:
        events_df (pd.DataFrame): DataFrame con eventos, debe incluir 'event', 'visitorid' y 'transactionid'.
        client_df (pd.DataFrame): DataFrame con datos de clientes, debe incluir 'id', 'nombre', 'apellido'.
        top_n (int): Número de clientes a mostrar en el top.
    """
    # Filtrar solo eventos de compra
    compras = events_df[events_df['event'] == 'transaction']

    # Contar compras por cliente
    compras_por_cliente = (
        compras.groupby('visitorid')['transactionid']
        .nunique()
        .sort_values(ascending=False)
        .to_frame(name='total_compras')
    )

    # Unir con datos de clientes
    merged_df = pd.merge(
        compras_por_cliente,
        client_df,
        left_on='visitorid',
        right_on='id',
        how='outer'
    )

    # Seleccionar y ordenar
    merged_df = (
        merged_df[['nombre', 'apellido', 'total_compras']]
        .sort_values(by='total_compras', ascending=False)
        .head(top_n)
    )

    # Crear el gráfico
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        x=merged_df['nombre'] + " " + merged_df['apellido'],  # nombre completo
        y=merged_df['total_compras'],
        palette='Blues_r',
        ax=ax
    )
    ax.set_xlabel("Cliente")
    ax.set_ylabel("Número de compras")
    ax.set_title(f"Top {top_n} Clientes con más compras")
    plt.xticks(rotation=45)

    # Mostrar en Streamlit
    st.pyplot(fig)

def top_brands_plot(product_df, brand_df, compras):
    # Unir productos con marcas
    productos_marcas = product_df.merge(brand_df, left_on='marca_id', right_on='id', how='left')

    # Contar compras por marca
    marcas_compradas = compras.merge(productos_marcas, left_on='itemid', right_on='id_x', how='left')
    marcas_count = marcas_compradas.groupby('marca')['transactionid'].nunique().sort_values(ascending=False)

    # Top 10 marcas
    top_brands = marcas_count.head(10)

    # Crear el gráfico
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=top_brands.values, y=top_brands.index, palette='Oranges_r', ax=ax)
    ax.set_xlabel("Número de compras")
    ax.set_ylabel("Marca")
    ax.set_title("Top 10 Marcas más populares")

    # Mostrar en Streamlit
    st.pyplot(fig)


def render_top_products_section(compras: pd.DataFrame, product_df: pd.DataFrame):    
    global category_df  # to access the category_df defined outside
    my_dict = dict(zip(category_df.iloc[:, 1], category_df.iloc[:, 0]))


    # --- Placeholder dropdown (not wired yet) ---
    # Later you'll fill options with real categories and filter the data below.
    selected_category = st.selectbox("Filtrar por categoría", my_dict.keys())  # placeholder
    st.caption("La lista de categorías se conectará después. Por ahora es solo UI.")

    # --- Compute top products (same logic you had) ---
    productos_comprados = (
        compras.groupby('itemid')['transactionid']
        .nunique()
        .sort_values(ascending=False)
    )

    top_products = (
        productos_comprados
        .reset_index()
        .merge(product_df[['id', 'nombre','categoria_id']], left_on='itemid', right_on='id', how='left')
    )

    if top_products.empty:
        st.info("No hay compras registradas para mostrar.")
        return
    
    if selected_category:
        category_id = my_dict[selected_category]
        top_products = top_products[top_products['categoria_id'] == category_id]

    top_products = top_products.head(10)

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x='transactionid', y='nombre', data=top_products, ax=ax, palette='Greens_r')
    ax.set_xlabel("Número de compras")
    ax.set_ylabel("Producto")
    ax.set_title("Top 10 Productos más vendidos")
    st.pyplot(fig)

st.subheader("Top Productos más Vendidos")
render_top_products_section(compras=compras, product_df=product_df)

st.subheader("Top Marcas más Populares")
top_brands_plot(product_df=product_df, brand_df=brand_df, compras=compras)

st.subheader("Top Clientes más Frecuentes")
plot_top_clients_streamlit(events_df=compras, client_df=client_df)

st.subheader("Distribución de eventos")
event_counts(events_df=events_df)