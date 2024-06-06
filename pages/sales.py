# import os
# import streamlit as st
# import pandas as pd


# output_dir = 'data'

# # Combine all the saved CSV files back into a single DataFrame
# all_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.startswith('category_summary_part_')]

# # Initialize an empty list to store DataFrames
# dataframes = []

# # Read each file and append to the list
# for file in all_files:
#     try:
#         df = pd.read_csv(file, encoding='UTF-8-SIG')
#         dataframes.append(df)
#     except Exception as e:
#         st.error(f"Error loading data from {file}: {e}")

# # Concatenate all DataFrames into a single DataFrame
# combined_df = pd.concat(dataframes, ignore_index=True)
# @st.cache_data
# def app():
#     st.title("Sales")
#     st.write("This is the Sales page.")
    

#     st.dataframe(combined_df.head())

        
    

  



# if __name__ == "__main__":
#     app()


# import os
# import streamlit as st
# import pandas as pd

# output_dir = 'data'

# @st.cache_data
# def load_combined_data():
#     # Combine all the saved CSV files back into a single DataFrame
#     all_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.startswith('category_summary_part_')]
    
#     # Initialize an empty list to store DataFrames
#     dataframes = []
    
#     # Read each file and append to the list
#     for file in all_files:
#         try:
#             df = pd.read_csv(file, encoding='UTF-8-SIG')
#             dataframes.append(df)
#         except Exception as e:
#             st.error(f"Error loading data from {file}: {e}")
    
#     # Concatenate all DataFrames into a single DataFrame
#     combined_df = pd.concat(dataframes, ignore_index=True)
#     return combined_df

# def app():
#     st.title("Sales")
#     st.write("This is the Sales page.")
    
#     # Initialize session state if not already done
#     if 'data_loaded' not in st.session_state:
#         st.session_state.data_loaded = False
    
#     # Button to trigger loading of the larger dataset
#     if not st.session_state.data_loaded:
#         if st.button("Load Larger Dataset"):
#             st.session_state.data_loaded = True
    
#     # Check if the data has been loaded and display it
#     if st.session_state.data_loaded:
#         with st.spinner("Loading large dataset..."):
#             combined_df = load_combined_data()
#             st.success("Larger Dataset Loaded Successfully!")
#             st.dataframe(combined_df.head())
#     else:
#         st.write("Click the button to load the larger dataset.")

# if __name__ == "__main__":
#     app()


## Best solution till Now

# import os
# import streamlit as st
# import pandas as pd
# import time

# output_dir = 'data'
# chunk_size = 10000  # Define the chunk size

# @st.cache_data
# def load_initial_chunk(file):
#     try:
#         chunk = pd.read_csv(file, encoding='UTF-8-SIG', chunksize=chunk_size)
#         return next(chunk)
#     except Exception as e:
#         st.error(f"Error loading initial chunk from {file}: {e}")
#         return pd.DataFrame()

# @st.cache_data
# def load_combined_data(existing_df, file):
#     try:
#         for chunk in pd.read_csv(file, encoding='UTF-8-SIG', chunksize=chunk_size):
#             existing_df = pd.concat([existing_df, chunk], ignore_index=True)
#             time.sleep(0.1)  # Simulate some delay for background processing
#     except Exception as e:
#         st.error(f"Error loading data from {file}: {e}")
#     return existing_df

# def app():
#     st.title("Sales")
#     st.write("This is the Sales page.")
    
#     # Initialize session state if not already done
#     if 'data_loaded' not in st.session_state:
#         st.session_state.data_loaded = False
#         st.session_state.first_chunk_loaded = False
#         st.session_state.existing_df = pd.DataFrame()
#         st.session_state.file_index = 0
    
#     # Get the list of files
#     all_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.startswith('category_summary_part_')]

#     # Button to trigger loading of the larger dataset
#     if not st.session_state.data_loaded:
#         if st.button("Load Larger Dataset"):
#             st.session_state.data_loaded = True
    
#     # Check if the data has been loaded and display it
#     if st.session_state.data_loaded and not st.session_state.first_chunk_loaded:
#         if all_files:
#             st.session_state.existing_df = load_initial_chunk(all_files[0])
#             st.session_state.first_chunk_loaded = True
#             st.session_state.file_index = 1
#             st.success("First chunk loaded successfully!")
#             st.dataframe(st.session_state.existing_df.head())
    
#     if st.session_state.first_chunk_loaded and st.session_state.file_index < len(all_files):
#         with st.spinner("Loading remaining data..."):
#             while st.session_state.file_index < len(all_files):
#                 st.session_state.existing_df = load_combined_data(st.session_state.existing_df, all_files[st.session_state.file_index])
#                 st.session_state.file_index += 1
#                 st.rerun()

# if __name__ == "__main__":
#     app()

# import os
# import streamlit as st
# import pandas as pd
# import time

# output_dir = 'data'
# chunk_size = 10000  # Define the chunk size

# @st.cache_data
# def load_initial_chunk(file):
#     try:
#         chunk = pd.read_csv(file, encoding='UTF-8-SIG', chunksize=chunk_size)
#         return next(chunk)
#     except Exception as e:
#         st.error(f"Error loading initial chunk from {file}: {e}")
#         return pd.DataFrame()

# @st.cache_data
# def load_combined_data(existing_df, file):
#     try:
#         for chunk in pd.read_csv(file, encoding='UTF-8-SIG', chunksize=chunk_size):
#             existing_df = pd.concat([existing_df, chunk], ignore_index=True)
#             time.sleep(0.1)  # Simulate some delay for background processing
#     except Exception as e:
#         st.error(f"Error loading data from {file}: {e}")
#     return existing_df

# def app():
#     st.title("Sales")
#     st.write("This is the Sales page.")
    
#     # Initialize session state if not already done
#     if 'data_loaded' not in st.session_state:
#         st.session_state.data_loaded = False
#         st.session_state.first_chunk_loaded = False
#         st.session_state.existing_df = pd.DataFrame()
#         st.session_state.file_index = 0
    
#     # Get the list of files
#     all_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.startswith('category_summary_part_')]

#     # Button to trigger loading of the larger dataset
#     if not st.session_state.data_loaded:
#         if st.button("Load Larger Dataset"):
#             st.session_state.data_loaded = True
    
#     # Check if the data has been loaded and display it
#     if st.session_state.data_loaded and not st.session_state.first_chunk_loaded:
#         if all_files:
#             st.session_state.existing_df = load_initial_chunk(all_files[0])
#             st.session_state.first_chunk_loaded = True
#             st.session_state.file_index = 1
#             st.success("First chunk loaded successfully!")
#             st.dataframe(st.session_state.existing_df.head())
    
#     if st.session_state.first_chunk_loaded and st.session_state.file_index < len(all_files):
#         with st.spinner("Loading remaining data..."):
#             while st.session_state.file_index < len(all_files):
#                 st.session_state.existing_df = load_combined_data(st.session_state.existing_df, all_files[st.session_state.file_index])
#                 st.session_state.file_index += 1

#     if st.session_state.first_chunk_loaded and st.session_state.file_index >= len(all_files):
#         st.success("All data loaded successfully!")
#         if st.button("Display all data"):
#             st.dataframe(st.session_state.existing_df)

# if __name__ == "__main__":
#     app()



# import os
# import streamlit as st
# import pandas as pd
# import time

# output_dir = 'data'
# chunk_size = 10000  # Define the chunk size

# @st.cache_data
# def load_initial_chunk(file):
#     try:
#         chunk = pd.read_csv(file, encoding='UTF-8-SIG', chunksize=chunk_size)
#         return next(chunk)
#     except Exception as e:
#         st.error(f"Error loading initial chunk from {file}: {e}")
#         return pd.DataFrame()

# @st.cache_data
# def load_combined_data(existing_df, file, _progress_bar):
#     try:
#         total_rows = sum(1 for _ in open(file, encoding='UTF-8-SIG'))
#         for i, chunk in enumerate(pd.read_csv(file, encoding='UTF-8-SIG', chunksize=chunk_size)):
#             existing_df = pd.concat([existing_df, chunk], ignore_index=True)
#             progress = (i + 1) * chunk_size / total_rows
#             _progress_bar.progress(progress)
#             time.sleep(0.1)  # Simulate some delay for background processing
#     except Exception as e:
#         st.error(f"Error loading data from {file}: {e}")
#     return existing_df

# def app():
#     st.title("Sales")
#     st.write("This is the Sales page.")
    
#     # Initialize session state if not already done
#     if 'data_loaded' not in st.session_state:
#         st.session_state.data_loaded = False
#         st.session_state.first_chunk_loaded = False
#         st.session_state.existing_df = pd.DataFrame()
#         st.session_state.file_index = 0
    
#     # Get the list of files
#     all_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.startswith('category_summary_part_')]

#     # Button to trigger loading of the larger dataset
#     if not st.session_state.data_loaded:
#         if st.button("Load Larger Dataset"):
#             st.session_state.data_loaded = True
    
#     # Check if the data has been loaded and display it
#     if st.session_state.data_loaded and not st.session_state.first_chunk_loaded:
#         if all_files:
#             st.session_state.existing_df = load_initial_chunk(all_files[0])
#             st.session_state.first_chunk_loaded = True
#             st.session_state.file_index = 1
#             st.success("First chunk loaded successfully!")
#             st.dataframe(st.session_state.existing_df.head())
    
#     if st.session_state.first_chunk_loaded and st.session_state.file_index < len(all_files):
#         progress_bar = st.progress(0)
#         with st.spinner("Loading remaining data..."):
#             while st.session_state.file_index < len(all_files):
#                 st.session_state.existing_df = load_combined_data(st.session_state.existing_df, all_files[st.session_state.file_index], progress_bar)
#                 st.session_state.file_index += 1

#     if st.session_state.first_chunk_loaded and st.session_state.file_index >= len(all_files):
#         st.success("All data loaded successfully!")
#         if st.button("Display all data"):
#             st.dataframe(st.session_state.existing_df)

# if __name__ == "__main__":
#     app()


# import os
# import streamlit as st
# import pandas as pd
# import time

# output_dir = 'data'
# chunk_size = 100000  # Define the chunk size

# @st.cache_data()
# def load_initial_chunk(file):
#     try:
#         chunk = pd.read_csv(file, encoding='UTF-8-SIG', chunksize=chunk_size)
#         return next(chunk)
#     except Exception as e:
#         st.error(f"Error loading initial chunk from {file}: {e}")
#         return pd.DataFrame()

# @st.cache_data
# def load_combined_data(existing_df, file, _progress_counter):
#     try:
#         existing_df = pd.concat([existing_df, pd.read_csv(file, encoding='UTF-8-SIG')], ignore_index=True)
#         _progress_counter.progress(1.0)
#         # time.sleep(0.1)  # Simulate some delay for background processing
#     except Exception as e:
#         st.error(f"Error loading data from {file}: {e}")
#     return existing_df

# def app():
#     st.title("Sales")
#     st.write("This is the Sales page.")
    
#     # Initialize session state if not already done
#     if 'data_loaded' not in st.session_state:
#         st.session_state.data_loaded = False
#         st.session_state.first_chunk_loaded = False
#         st.session_state.existing_df = pd.DataFrame()
#         st.session_state.file_index = 0
    
#     # Get the list of files
#     all_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.startswith('category_summary_part_')]

#     # Button to trigger loading of the larger dataset
#     if not st.session_state.data_loaded:
#         if st.button("Load Larger Dataset"):
#             st.session_state.data_loaded = True
    
#     # Check if the data has been loaded and display it
#     if st.session_state.data_loaded and not st.session_state.first_chunk_loaded:
#         if all_files:
#             st.session_state.existing_df = load_initial_chunk(all_files[0])
#             st.session_state.first_chunk_loaded = True
#             st.session_state.file_index = 1
#             st.success("First chunk loaded successfully!")
#             st.dataframe(st.session_state.existing_df.head())
    
#     if st.session_state.first_chunk_loaded and st.session_state.file_index < len(all_files):
#         progress_counter = st.progress(0)
#         with st.spinner("Loading remaining data..."):
#             while st.session_state.file_index < len(all_files):
#                 st.session_state.existing_df = load_combined_data(st.session_state.existing_df, all_files[st.session_state.file_index], progress_counter)
#                 st.session_state.file_index += 1
#                 progress_percentage = min((st.session_state.file_index / len(all_files)) * 100, 100)
#                 progress_counter.progress(progress_percentage / 100)

#     if st.session_state.first_chunk_loaded and st.session_state.file_index >= len(all_files):
#         st.success("All data loaded successfully!")
#         if st.button("Display all data"):
#             st.dataframe(st.session_state.existing_df)

# if __name__ == "__main__":
#     app()


# import os
# import streamlit as st
# import pandas as pd

# output_dir = 'data'
# chunk_size = 100000  # Define the chunk size

# @st.cache_data
# def load_initial_chunk(file):
#     try:
#         chunk = pd.read_csv(file, encoding='UTF-8-SIG', chunksize=chunk_size)
#         return next(chunk)
#     except Exception as e:
#         st.error(f"Error loading initial chunk from {file}: {e}")
#         return pd.DataFrame()

# @st.cache_data
# def load_combined_data(existing_df, file, date1_timestamp, date2_timestamp):
#     try:
#         chunk = pd.read_csv(file, encoding='UTF-8-SIG')
#         chunk['event_time'] = pd.to_datetime(chunk['event_time'])

#         # Apply date filter
#         if date1_timestamp and date2_timestamp:
#             chunk = chunk[(chunk['event_time'] >= date1_timestamp) & (chunk['event_time'] <= date2_timestamp)]

#         existing_df = pd.concat([existing_df, chunk], ignore_index=True)
#     except Exception as e:
#         st.error(f"Error loading data from {file}: {e}")
#     return existing_df

# def app():
#     st.title("Sales")
#     st.write("This is the Sales page.")
    
#     # Initialize session state if not already done
#     if 'data_loaded' not in st.session_state:
#         st.session_state.data_loaded = False
#         st.session_state.first_chunk_loaded = False
#         st.session_state.existing_df = pd.DataFrame()
#         st.session_state.file_index = 0
    
#     # Get the list of files
#     all_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.startswith('category_summary_part_')]

#     # Get the selected date range from session state
#     date1, date2 = st.session_state.get('selected_dates', (None, None))
#     date1_timestamp = pd.Timestamp(date1) if date1 else None
#     date2_timestamp = pd.Timestamp(date2) if date2 else None

#     # Button to trigger loading of the larger dataset
#     if not st.session_state.data_loaded:
#         if st.button("Load Larger Dataset"):
#             st.session_state.data_loaded = True
    
#     # Check if the data has been loaded and display it
#     if st.session_state.data_loaded and not st.session_state.first_chunk_loaded:
#         if all_files:
#             st.session_state.existing_df = load_initial_chunk(all_files[0])
#             st.session_state.first_chunk_loaded = True
#             st.session_state.file_index = 1
#             st.success("First chunk loaded successfully!")
#             st.dataframe(st.session_state.existing_df.head())
    
#     if st.session_state.first_chunk_loaded and st.session_state.file_index < len(all_files):
#         progress_counter = st.progress(0)
#         with st.spinner("Loading remaining data..."):
#             while st.session_state.file_index < len(all_files):
#                 st.session_state.existing_df = load_combined_data(
#                     st.session_state.existing_df,
#                     all_files[st.session_state.file_index],
#                     date1_timestamp,
#                     date2_timestamp
#                 )
#                 st.session_state.file_index += 1
#                 progress_percentage = min((st.session_state.file_index / len(all_files)) * 100, 100)
#                 progress_counter.progress(progress_percentage / 100)

#     if st.session_state.first_chunk_loaded and st.session_state.file_index >= len(all_files):
#         st.success("All data loaded successfully!")
#         if st.button("Display all data"):
#             st.dataframe(st.session_state.existing_df)

# if __name__ == "__main__":
#     app()



# import os
# import streamlit as st
# import pandas as pd

# df = pd.read_pickle('data/all_data_part_1.pkl', compression='gzip')



# def app():
#     st.title("Sales")
#     st.write("This is the Sales page.")
#     st.dataframe(df)


# if __name__ == "__main__":
#     app()


import os
import streamlit as st
import pandas as pd

output_dir = 'data'

@st.cache_data
def load_initial_chunk(file):
    try:
        chunk = pd.read_pickle(file, compression='gzip')
        return chunk
    except Exception as e:
        st.error(f"Error loading initial chunk from {file}: {e}")
        return pd.DataFrame()

@st.cache_data
def load_combined_data(existing_df, file, date1_timestamp, date2_timestamp):
    try:
        chunk = pd.read_pickle(file, compression= 'gzip')
        chunk['event_time'] = pd.to_datetime(chunk['event_time'])

        # Apply date filter
        if date1_timestamp and date2_timestamp:
            chunk = chunk[(chunk['event_time'] >= date1_timestamp) & (chunk['event_time'] <= date2_timestamp)]

        existing_df = pd.concat([existing_df, chunk], ignore_index=True)
    except Exception as e:
        st.error(f"Error loading data from {file}: {e}")
    return existing_df

def app():
    st.title("Sales")
    st.write("This is the Sales page.")
    
    # Initialize session state if not already done
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
        st.session_state.first_chunk_loaded = False
        st.session_state.existing_df = pd.DataFrame()
        st.session_state.file_index = 0
    
    # Get the list of files
    all_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.startswith('all_data_cart') and file.endswith('.pkl')]

    # Get the selected date range from session state
    date1, date2 = st.session_state.get('selected_dates', (None, None))
    date1_timestamp = pd.Timestamp(date1) if date1 else None
    date2_timestamp = pd.Timestamp(date2) if date2 else None

    # Button to trigger loading of the larger dataset
    if not st.session_state.data_loaded:
        if st.button("Load Larger Dataset"):
            st.session_state.data_loaded = True
    
    # Check if the data has been loaded and display it
    if st.session_state.data_loaded and not st.session_state.first_chunk_loaded:
        if all_files:
            st.session_state.existing_df = load_initial_chunk(all_files[0])
            st.session_state.first_chunk_loaded = True
            st.session_state.file_index = 1
            st.success("First chunk loaded successfully!")
            st.dataframe(st.session_state.existing_df.head())
    
    if st.session_state.first_chunk_loaded and st.session_state.file_index < len(all_files):
        progress_counter = st.progress(0)
        with st.spinner("Loading remaining data..."):
            while st.session_state.file_index < len(all_files):
                st.session_state.existing_df = load_combined_data(
                    st.session_state.existing_df,
                    all_files[st.session_state.file_index],
                    date1_timestamp,
                    date2_timestamp
                )
                st.session_state.file_index += 1
                progress_percentage = min((st.session_state.file_index / len(all_files)) * 100, 100)
                progress_counter.progress(progress_percentage / 100)

    if st.session_state.first_chunk_loaded and st.session_state.file_index >= len(all_files):
        st.success("All data loaded successfully!")
        if st.button("Display all data"):
            st.dataframe(st.session_state.existing_df)

if __name__ == "__main__":
    app()
