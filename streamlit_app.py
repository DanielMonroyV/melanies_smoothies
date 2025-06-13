# Import Python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# UI title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: name for order
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Load fruit options with SEARCH_ON column
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"), col("SEARCH_ON")
)

# Convert Snowpark to Pandas
pd_df = my_dataframe.to_pandas()

# Multiselect input
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"],
    max_selections=5
)

# Show nutrition info and prepare insert
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Buscar el valor SEARCH_ON asociado al FRUIT_NAME
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        # Subtítulo personalizado
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Obtener datos desde la API
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            fruityvice_response.raise_for_status()
            fruit_data = fruityvice_response.json()
            st.dataframe(fruit_data, use_container_width=True)
        except Exception as e:
            st.error("Sorry, that fruit is not in our database.")

    # SQL INSERT con ingredientes y nombre
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string.strip()}', '{name_on_order}')
    """

    # Botón para insertar
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
