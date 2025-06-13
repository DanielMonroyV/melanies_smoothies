# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session

# Conexión con Snowflake (reemplaza con tu lógica de conexión si es diferente)
cnx = st.connection("snowflake")
session = cnx.session()

# UI
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Load fruit options desde Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_options = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Multiselect con límite de 5 ingredientes
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# Lógica de inserción y visualización
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Mostrar encabezado por fruta
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Llamada a la API externa
        url = f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
        response = requests.get(url)

        # Validar si la fruta está disponible
        if response.status_code == 200:
            try:
                sf_df = st.dataframe(data=response.json(), use_container_width=True)
            except Exception:
                st.error("⚠️ Error displaying the fruit data.")
        else:
            st.dataframe({"value": ["Sorry, that fruit is not in our database."]})

    # Botón para enviar la orden
    if st.button("Submit Order"):
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
