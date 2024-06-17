import os
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import statsmodels.api as sm
import math




def app():
    st.title("Univariate Analysis")

    st.write("We're working hard to bring you something amazing! :rocket:")

    st.write("Stay tuned for updates.")

    # Replace 'https://example.com/coming_soon_image.png' with your actual image URL from Splash or any other source
    image_url = 'https://images.unsplash.com/photo-1614332287897-cdc485fa562d?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8Y29taW5nJTIwc29vbnxlbnwwfHwwfHx8MA%3D%3D'

    st.image(image_url, use_column_width=True)



if __name__ == "__main__":
    app()