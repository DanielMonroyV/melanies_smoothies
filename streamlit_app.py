# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# UI title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Load fruit options with search alias
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Multiselect for ingredients with max 5
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.to_pandas()["FRUIT_NAME"].tolist(),  # show FRUIT_NAME to users
    max_selections=5
)

# Logic for inserting and displaying nutrition info
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get corresponding search_on value
        fruit_row = my_dataframe.filter(col("FRUIT_NAME") == fruit_chosen).collect()[0]
        fruit_search_name = fruit_row["SEARCH_ON"]

        st.subheader(fruit_chosen + ' Nutrition Information')

        # API call to SmoothieFroot
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_search_name}")
            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.dataframe(data={"value": ["Sorry, that fruit is not in our database."]})
        except Exception as e:
            st.error(f"Error retrieving data for {fruit_chosen}: {e}")

    # Insert order into Snowflake
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
