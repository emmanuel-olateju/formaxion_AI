import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Function to generate random data
def generate_random_data(n):
    data = {
        'prompt_tokens': np.random.randint(100, 1000, size=n),
        'completion_tokens': np.random.randint(100, 1000, size=n),
        'total_tokens': np.random.randint(200, 2000, size=n),
        'dollar_cost': np.random.uniform(100, 500, size=n)
    }
    return pd.DataFrame(data)

# Generate some random data
data = generate_random_data(50)

# Streamlit app
st.title('Token Visualization App')

# Display the dataframe
st.subheader('Sample Data')
st.write(data)

# Plotting
st.subheader('Token Metrics Visualization')

# Plot prompt_tokens, completion_tokens, total_tokens against index as line plots
fig1 = px.line(data, x=data.index, y=['prompt_tokens', 'completion_tokens', 'total_tokens'],
               title='Token Metrics Over Index')
st.plotly_chart(fig1)

# Plot dollar_cost against index as a bar plot
fig2 = px.bar(data, x=data.index, y='dollar_cost', title='Dollar Cost Over Index')
st.plotly_chart(fig2)
