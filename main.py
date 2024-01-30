import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
# URL of the webpage containing the table
url = 'https://www.myfxbook.com/community/outlook/EURUSD'
def update_data():
    # Send a GET request
    response = requests.get(url)
    # print(response)
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table with the specific ID
    table = soup.find('table', {'id': 'currentMetricsTable'})

    # Extract the data and headers
    rows = table.find_all('tr')
    headers = [header.text for header in rows[0].find_all('th')]
    data = [[cell.text for cell in row.find_all('td')] for row in rows[1:]]
    # print(data)

    # Function to clean each cell in the data
    def clean_cell(cell):
        # Remove newlines and leading/trailing whitespace
        cell = cell.strip().replace('\n', '')
        
        # Remove specific unwanted characters
        cell = cell.replace('%', '').replace('lots', '').strip()

        # Convert to float or int if possible
        try:
            cell = float(cell)
            if cell.is_integer():
                return int(cell)
            return cell
        except ValueError:
            return cell

    # Apply the cleaning function to each cell
    cleaned_data = [[clean_cell(cell) for cell in row] for row in data]

    # print(cleaned_data)


    # print(headers)
    # Convert to DataFrame
    df = pd.DataFrame(cleaned_data, columns=["Position","Percentage","Lots","Number"])

    # print(df)
    return df


# # Set up the plot
# plt.ion()  # Turn on interactive mode
# fig, ax = plt.subplots()

# while True:
#     # Update the data
#     df = update_data()

#     # Clear the current plot
#     ax.clear()

#     # Create the bar plot
#     ax.bar(df['Position'], df['Percentage'], color=['blue', 'orange'])

#     # Set plot title and labels
#     ax.set_title('Live Bar Chart of Positions')
#     ax.set_xlabel('Position')
#     ax.set_ylabel('Percentage')

#     # Draw the plot
#     plt.draw()

#     # Pause for a brief period (e.g., 1 second)
#     plt.pause(1)



# # Streamlit app layout
# st.title('Live Bar Chart of Positions')

# # Container to hold the chart
# chart = st.empty()
# import time
# while True:
#     # Update the data
#     try:
#         df = update_data()

#         # Plot the chart
#         chart.bar_chart(df.set_index('Position'))

#         # Sleep for some time (e.g., 1 second)
#         time.sleep(5)
#     except Exception as e:
#         print(e)
#         time.sleep(10)


# File to store data
data_file = 'data.csv'
import os
# Function to read data from file or create a new DataFrame if file doesn't exist
def read_data(file_name):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        return pd.DataFrame({'Time': [], 'Position': [], 'Percentage': [], 'Lots':[], 'Number':[]})


# Function to append new data and save to file
def append_data(df, new_data):
    current_time = pd.Timestamp.now()
    new_row = {'Time': current_time, **new_data}
    df = pd.concat([df,pd.DataFrame(new_row)], ignore_index=True)
    df.to_csv(data_file, index=False)
    return df

# Streamlit app layout
# st.title('Live Line Chart of Positions')

# Read existing data
df = read_data(data_file)

st.title('Live Line Chart of Buy and Sell Positions')
# Container to hold the chart
chart = st.empty()
import time
# Update loop
# while True:
#     # Generate and append new data
#     new_data = update_data()
#     df = append_data(df, new_data)
#     print(df)
#     # Plot the line chart
#     # pivot_df = df.pivot(index='Time', columns='Position', values='Lots')
#     pivot_df = df.pivot_table(index='Time', columns='Position', values='Lots', aggfunc='mean')

#     print(pivot_df)
#     # Streamlit app layout

#     # Plot the line chart
#     chart.line_chart(pivot_df)

#     # Sleep for some time (e.g., 5 seconds)
#     time.sleep(5)


import matplotlib.dates as mdates

# while True:
#     # Generate and append new data
#     new_data = update_data()  # Make sure this function returns the new data
#     df = append_data(df, new_data)  # Append new data to the DataFrame

#     # Pivot the DataFrame for the line chart
#     pivot_df = df.pivot_table(index='Time', columns='Position', values='Lots', aggfunc='mean')

#     # Create a Matplotlib plot
#     fig, ax = plt.subplots()
#     ax.plot(pivot_df.index, pivot_df['Short'], label='Short')
#     ax.plot(pivot_df.index, pivot_df['Long'], label='Long')

#     # Format the x-axis for timestamps
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
#     plt.xticks(rotation=45)
#     plt.tight_layout()

#     # Add labels and legend
#     ax.set_xlabel('Time')
#     ax.set_ylabel('Lots')
#     ax.legend()

#     # Display the plot in Streamlit
#     chart.pyplot(fig)

#     # Sleep for some time (e.g., 5 seconds)
#     time.sleep(5)


while True:
    # Generate and append new data
    new_data = update_data()  # Make sure this function returns the new data
    df = append_data(df, new_data)  # Append new data to the DataFrame

    # Pivot the DataFrame for the line chart
    pivot_df = df.pivot_table(index='Time', columns='Position', values='Lots', aggfunc='mean')
    pivot_df.index = pd.to_datetime(pivot_df.index)
    # print("df info:",pivot_df.info())
    
    pivot_df.sort_index(inplace=True)

    pivot_df = pivot_df[-200:]
    # Create a Matplotlib plot with dual axes
    fig, ax1 = plt.subplots()
    # Plot 'Buy' position on the primary y-axis
    color = 'tab:blue'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Buy Lots', color=color)
    ax1.plot(pivot_df.index, pivot_df['Long'], label='Long', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45)

    # Create a second y-axis for 'Sell' position
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:red'
    ax2.set_ylabel('Short Lots', color=color)  # we already handled the x-label with ax1
    ax2.plot(pivot_df.index, pivot_df['Short'], label='Short', color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    # Add title and layout adjustments
    plt.title('Long and Short Positions Over Time')
    plt.tight_layout()

    # Display the plot in Streamlit
    chart.pyplot(fig)
    # chart.line_chart(pivot_df)
    # Sleep for some time (e.g., 5 seconds)
    time.sleep(30)