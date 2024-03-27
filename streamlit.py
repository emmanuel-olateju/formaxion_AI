import streamlit as st
import requests
import copy

import os
import json
import yaml

with open("params.yaml", 'r') as file:
  # Read the file contents
  params = yaml.safe_load(file)

# Streamlit app layout
def main():

    st.title("Test formaxionAI")

    if 'username' not in st.session_state:
        response = requests.post(params['NEW_CHAT_URL'],json={'username':'test_user'})
        assert response.status_code == 200
        response = response.json()
        st.session_state['username'] = response['username']
        st.session_state['thread_id'] = response['thread_id']
    
    if chat_input:=st.chat_input('Hello, how do you want me to help you today?'):
        response = requests.post(params['CHAT_URL'],json={
            'username':st.session_state['username'],
            'thread_id':st.session_state['thread_id'],
            'message':chat_input
        })
        assert response.status_code == 200
        response = response.json()
        chats_responses = response['messages']
        for message in chats_responses:
            with st.chat_message(message['role']):
                st.write(message['content'])


if __name__ == "__main__":
    main()
