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



# from dask.distributed import Client
# # Ensure the environment variable is set for Modin to use Dask
# os.environ["MODIN_ENGINE"] = "dask"

# # Initialize the Dask client with an appropriate memory limit
# client = Client(memory_limit='4GB')  # Adjust memory limit as needed
# import modin.pandas as pd  # Use Modin with Dask
# import os
# import streamlit as st
# import dask.dataframe as dd

# @st.cache_data
# def load_data(file_path):
#     """
#     Load data from a file in the data directory using Dask.
    
#     Parameters:
#     file_path (str): The path to the file to load.
    
#     Returns:
#     pd.DataFrame: The loaded data as a DataFrame.
#     """
#     print(file_path)
#     try:
#         # Try to read the data using Dask directly
#         df = dd.read_parquet(file_path, compression='gzip')
#         data_path = os.path.join(os.path.dirname(__file__), '..', 'data', file_path)
#     except Exception as e:
#         st.error(f"Error loading data with Dask: {e}")
#         df = None  # Return None if loading fails
    
#     return df


# import os
# import streamlit as st
# import dask.dataframe as dd
# import pandas as pd

# @st.cache_data
# def load_data(file_path):
#     """
#     Load data from a file in the data directory using Dask.
    
#     Parameters:
#     file_path (str): The path to the file to load.
    
#     Returns:
#     pd.DataFrame: The loaded data as a DataFrame.
#     """
#     try:
#         data_path = os.path.join(os.path.dirname(__file__), '..', 'data', file_path)
#         df = dd.read_parquet(data_path, compression='gzip')
#     except Exception as e:
#         st.error(f"Error loading data with Dask: {e}")
#         df = pd.DataFrame()  # Return an empty DataFrame if loading fails
    
#     return df
