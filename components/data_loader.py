# import os
# import streamlit as st

# # Ensure the environment variable is set for Modin to use Ray
# os.environ["MODIN_ENGINE"] = "dask"  # or "dask"

# import modin.pandas as pd  # Use Modin instead of pandas



# # Define a custom hash function for DeltaGenerator
# # def my_hash_func(obj):
# #     return hash(id(obj))

# # # Function to load data
# @st.cache_data
# def load_data(file_name):
#     """
#     Load data from a file in the data directory.
    
#     Parameters:
#     file_name (str): The name of the file to load.
    
#     Returns:
#     pd.DataFrame: The loaded data as a DataFrame.
#     """
#     data_path = os.path.join(os.path.dirname(__file__), '..', 'data', file_name)
#     return pd.read_pickle(data_path, compression='gzip')


import os
import streamlit as st
import dask.dataframe as dd
from dask.distributed import Client
# Ensure the environment variable is set for Modin to use Dask
os.environ["MODIN_ENGINE"] = "dask"

# Initialize the Dask client with an appropriate memory limit
client = Client(memory_limit='4GB')  # Adjust memory limit as needed
import modin.pandas as pd  # Use Modin with Dask


@st.cache_data
def load_data(file_name):
    """
    Load data from a file in the data directory using Modin with Dask.
    
    Parameters:
    file_name (str): The name of the file to load.
    
    Returns:
    pd.DataFrame: The loaded data as a DataFrame.
    """
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', file_name)
    try:
        # Try to read the data using Modin (which uses Dask)
        df = pd.read_pickle(data_path, compression='gzip')
    except Exception as e:
        st.error(f"Error loading data with Modin: {e}. Falling back to Dask.")
        # Fallback to Dask if Modin fails
        df = dd.read_pickle(data_path, compression='gzip')
    
    return df