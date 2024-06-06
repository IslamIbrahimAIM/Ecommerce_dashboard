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


# import os
# import streamlit as st
# import pandas as pd

# output_dir = 'data'

# @st.cache_data
# def load_initial_chunk(file):
#     try:
#         chunk = pd.read_pickle(file, compression='gzip')
#         return chunk
#     except Exception as e:
#         st.error(f"Error loading initial chunk from {file}: {e}")
#         return pd.DataFrame()

# # @st.cache_data
# # def load_combined_data(existing_df, file, date1_timestamp, date2_timestamp):
# #     try:
# #         chunk = pd.read_pickle(file, compression= 'gzip')
# #         chunk['event_time'] = pd.to_datetime(chunk['event_time'])

# #         # Apply date filter
# #         if date1_timestamp and date2_timestamp:
# #             chunk = chunk[(chunk['event_time'] >= date1_timestamp) & (chunk['event_time'] <= date2_timestamp)]

# #         existing_df = pd.concat([existing_df, chunk], ignore_index=True)
# #     except Exception as e:
# #         st.error(f"Error loading data from {file}: {e}")
# #     return existing_df

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
#     all_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.startswith('all_data_cart') and file.endswith('.pkl')]

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

# output_dir = 'data'
# data_file = os.path.join(output_dir, 'all_data_cart.pkl')  # Adjust the file name as necessary

# @st.cache_data
# def load_data(file):
#     try:
#         data = pd.read_pickle(file, compression='gzip')
#         return data
#     except Exception as e:
#         st.error(f"Error loading data from {file}: {e}")
#         return pd.DataFrame()

# def app():
#     def filter_data(df, start_date, end_date):
#         try:
#             df['event_time'] = pd.to_datetime(df['event_time'])
#             if start_date and end_date:
#                 start_timestamp = pd.Timestamp(start_date)
#                 end_timestamp = pd.Timestamp(end_date)
#                 df = df[(df['event_time'] >= start_timestamp) & (df['event_time'] <= end_timestamp)].copy()
#             return df
#         except Exception as e:
#             st.error(f"Error filtering data: {e}")
#             return df

#     st.title("Sales")
#     st.write("This is the Sales page.")
    
#     # Load the data once when the script runs
#     data = load_data(data_file)
    
#     # Get the selected date range from session state
#     date1, date2 = st.session_state.get('selected_dates', (None, None))
    
#     # Filter data based on selected dates
#     filtered_data = filter_data(data, date1, date2)
    
#     # Display the data
#     st.dataframe(filtered_data)
#     st.success("Data loaded and filtered successfully!")

# if __name__ == "__main__":
#     app()


# import os
# import streamlit as st
# import pandas as pd
# import plotly.express as px

# output_dir = 'data'
# data_file = os.path.join(output_dir, 'all_data_cart.pkl')  # Adjust the file name as necessary

# @st.cache_data
# def load_data(file):
#     try:
#         data = pd.read_pickle(file, compression='gzip')
#         return data
#     except Exception as e:
#         st.error(f"Error loading data from {file}: {e}")
#         return pd.DataFrame()

# def app():
#     st.title("Sales")
#     st.write("This is the Sales page.")
    
#     # Load the data once when the script runs
#     data = load_data(data_file)
    
#     # Get the selected date range from session state
#     date1, date2 = st.session_state.get('selected_dates', (None, None))
    
#     # Convert the date strings to pandas Timestamp objects
#     date1_timestamp = pd.Timestamp(date1) if date1 else None
#     date2_timestamp = pd.Timestamp(date2) if date2 else None
    
#     # Filter data based on selected dates
#     if date1_timestamp and date2_timestamp:
#         if date1_timestamp == date2_timestamp:
#             # Filter for a single day
#             filtered_data = data[data['event_time'].dt.date == date1_timestamp.date()].copy()
#         else:
#             # Filter for a date range
#             filtered_data = data[(data['event_time'] >= date1_timestamp) & (data['event_time'] <= date2_timestamp + pd.Timedelta(days=1))].copy()
#     else:
#         filtered_data = data.copy()

#     filtered_data['date'] = filtered_data['event_time'].dt.date
#     grouped_data_cat = filtered_data.groupby(['category', 'date'], observed=False).agg(
#         views = ('user_session', 'nunique'),
#         visitors = ('user_id', 'nunique')
#     ).reset_index()
#     grouped_data_cat_no = grouped_data_cat.groupby(['category'], observed=False).agg(
#         views = ('views', 'sum'),
#         visitors = ('visitors', 'sum')
#     ).reset_index()
    
#     # Display the data
#     st.dataframe(grouped_data_cat)
#     st.success("Data loaded and filtered successfully!")

#     # Plotting the data
#     st.bar_chart(grouped_data_cat,  x='date', y=['visitors', 'views'], color='category')
#     grouped_data_cat_sorted = grouped_data_cat_no.sort_values(by='views', ascending=False)
#     fig_views = px.bar(grouped_data_cat_sorted, 
#                    x='category', 
#                    y='views', 
#                    title='Number of Views by Category',
#                    labels={'Number_of_views': 'Number of Views', 'category': 'Category'},
#                    color='category')

#     # Automatically format the text
#     fig_views.update_traces(texttemplate='%{y:.2s}', textposition='outside')

#     fig_views.update_layout(
#         # width=1000,  # Increase width
#         height=600,   # Increase height
#         margin=dict(l=20, r=20, t=50, b=20)
#     )

#     st.plotly_chart(fig_views)


# if __name__ == "__main__":
#     app()


# import os
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go

# output_dir = 'data'
# data_file = os.path.join(output_dir, 'all_data_cart.pkl')  # Adjust the file name as necessary

# @st.cache_data
# def load_data(file):
#     try:
#         data = pd.read_pickle(file, compression='gzip')
#         return data
#     except Exception as e:
#         st.error(f"Error loading data from {file}: {e}")
#         return pd.DataFrame()

# def app():
#     st.title("Sales")
#     st.write("This is the Sales page.")
    
#     # Load the data once when the script runs
#     data = load_data(data_file)
    
#     # Get the selected date range from session state
#     date1, date2 = st.session_state.get('selected_dates', (None, None))
    
#     # Convert the date strings to pandas Timestamp objects
#     date1_timestamp = pd.Timestamp(date1) if date1 else None
#     date2_timestamp = pd.Timestamp(date2) if date2 else None
    
#     # Filter data based on selected dates
#     if date1_timestamp and date2_timestamp:
#         if date1_timestamp == date2_timestamp:
#             # Filter for a single day
#             filtered_data = data[data['event_time'].dt.date == date1_timestamp.date()].copy()
#         else:
#             # Filter for a date range
#             filtered_data = data[(data['event_time'] >= date1_timestamp) & (data['event_time'] <= date2_timestamp + pd.Timedelta(days=1))].copy()
#     else:
#         filtered_data = data.copy()

#     filtered_data['date'] = filtered_data['event_time'].dt.date
#     grouped_data_cat = filtered_data.groupby(['category', 'date'], observed=False).agg(
#         views=('user_session', 'nunique'),
#         visitors=('user_id', 'nunique')
#     ).reset_index()
#     grouped_data_cat_no = grouped_data_cat.groupby(['category'], observed=False).agg(
#         views=('views', 'sum'),
#         visitors=('visitors', 'sum')
#     ).reset_index()
    
#     # Display the data
#     st.dataframe(grouped_data_cat)
#     st.success("Data loaded and filtered successfully!")

#     # Plotting the data
#     st.bar_chart(grouped_data_cat,  x='date', y=['visitors', 'views'], color='category')
#     grouped_data_cat_sorted = grouped_data_cat_no.sort_values(by='views', ascending=False)
    
#     fig_views = px.bar(grouped_data_cat_sorted, 
#                        x='category', 
#                        y='views', 
#                        title='Number of Views by Category',
#                        labels={'views': 'Number of Views', 'category': 'Category'},
#                        color='category')

#     # Automatically format the text
#     fig_views.update_traces(texttemplate='%{y:.2s}', textposition='outside')

#     fig_views.update_layout(
#         height=600,   # Increase height
#         margin=dict(l=20, r=20, t=50, b=20)
#     )

#     st.plotly_chart(fig_views, use_container_width=True)

#     # Add a Plotly click event handler
#     selected_category = st.session_state.get('selected_category', None)

#     if 'click_data' not in st.session_state:
#         st.session_state['click_data'] = None

#     def click_event(trace, points, selector):
#         if points.point_inds:
#             st.session_state['click_data'] = points
#             selected_category = points[0]['x']
#             st.session_state['selected_category'] = selected_category

#     fig_views.data[0].on_click(click_event)

#     if selected_category:
#         st.write(f"Selected category: {selected_category}")
#         category_data = grouped_data_cat[grouped_data_cat['category'] == selected_category]

#         fig_detail = px.line(category_data, 
#                              x='date', 
#                              y='views', 
#                              title=f'Performance for {selected_category} per Date',
#                              labels={'views': 'Number of Views', 'date': 'Date'})

#         st.plotly_chart(fig_detail, use_container_width=True)

# if __name__ == "__main__":
#     app()

import os
import streamlit as st
import pandas as pd
import plotly.express as px

output_dir = 'data'
data_file = os.path.join(output_dir, 'all_data_cart.pkl')  # Adjust the file name as necessary
all_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.startswith('all_data_sessions_cat_') and file.endswith('.pkl')]

@st.cache_data
def load_data(file):
    try:
        data = pd.read_pickle(file, compression='gzip')
        return data
    except Exception as e:
        st.error(f"Error loading data from {file}: {e}")
        return pd.DataFrame()

@st.cache_data
def load_all_files(files):
    data_list = []
    for file in files:
        try:
            data = pd.read_pickle(file, compression='gzip')
            data_list.append(data)
        except Exception as e:
            st.error(f"Error loading data from {file}: {e}")
    if data_list:
        combined_data = pd.concat(data_list, ignore_index=True)
        return combined_data
    else:
        return pd.DataFrame()

def app():
    st.title("Sales")
    st.write("This is the Sales page.")
    
    # Load the data once when the script runs
    data = load_data(data_file)
    
    # Get the selected date range from session state
    date1, date2 = st.session_state.get('selected_dates', (None, None))
    
    # Convert the date strings to pandas Timestamp objects
    date1_timestamp = pd.Timestamp(date1) if date1 else None
    date2_timestamp = pd.Timestamp(date2) if date2 else None
    
    # Filter data based on selected dates
    if date1_timestamp and date2_timestamp:
        if date1_timestamp == date2_timestamp:
            # Filter for a single day
            filtered_data = data[data['event_time'].dt.date == date1_timestamp.date()].copy()
        else:
            # Filter for a date range
            filtered_data = data[(data['event_time'] >= date1_timestamp) & (data['event_time'] <= date2_timestamp + pd.Timedelta(days=1))].copy()
    else:
        filtered_data = data.copy()

    filtered_data['date'] = filtered_data['event_time'].dt.date
    grouped_data_cat = filtered_data.groupby(['category', 'date'], observed=False).agg(
        views=('user_session', 'nunique'),
        visitors=('user_id', 'nunique')
    ).reset_index()
    grouped_data_cat_no = grouped_data_cat.groupby(['category'], observed=False).agg(
        views=('views', 'sum'),
        visitors=('visitors', 'sum')
    ).reset_index()

    grouped_data_cat_no_sorted = grouped_data_cat_no.sort_values(by='views', ascending=False)
    
    # Display the data
    st.dataframe(grouped_data_cat)
    st.success("Data loaded and filtered successfully!")

    # Plotting the summary data
    fig_views = px.bar(grouped_data_cat_no_sorted, 
                       x='category', 
                       y='views', 
                       title='Number of Views by Category',
                       labels={'views': 'Number of Views', 'category': 'Category'},
                       color='category')

    # Automatically format the text
    fig_views.update_traces(texttemplate='%{y:.2s}', textposition='outside')

    fig_views.update_layout(
        height=600,   # Increase height
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig_views, use_container_width=True)

    # Add a selectbox for categories
    selected_category = st.selectbox(
        "Select a category to view details",
        options=grouped_data_cat_no_sorted['category'].unique()
    )

    if selected_category:
        category_data = grouped_data_cat[grouped_data_cat['category'] == selected_category]

        fig_detail = px.line(category_data, 
                             x='date', 
                             y='views', 
                             title=f'Performance for {selected_category} per Date',
                             labels={'views': 'Number of Views', 'date': 'Date'})

        st.plotly_chart(fig_detail, use_container_width=True)

        data_additional = load_all_files(all_files)
        st.dataframe(data_additional.head())

if __name__ == "__main__":
    app()



