import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import os

response = requests.get(os.environ.get("ADMIN_FETCH_TOKEN_CONSUMPTION"))
assert response.status_code==200
data = pd.DataFrame(response.json()['tokens_times'])
data['time'] = pd.to_datetime(data['time'])
data = data.sort_values(by='time')
# st.write(data)

# Display the dataframe
# st.subheader('Sample Data')
# st.write(data)

# Plotting
# st.subheader('Token Metrics Visualization')

# Plot prompt_tokens, completion_tokens, total_tokens against index as line plots
# fig1 = px.line(data, x=data.index, y=['prompt_tokens', 'completion_tokens', 'total_tokens'],
#                title='Token Metrics Over Index')
# st.plotly_chart(fig1)

# Plot dollar_cost against index as a bar plot
fig2 = px.bar(data, x=data['time'], y='tokens', title='Token Cost OVer Time')
st.plotly_chart(fig2)
