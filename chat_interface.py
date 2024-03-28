import streamlit as st
import requests
import copy

import os
import json
import yaml

with open("api_urls.yml", 'r') as file:
  api_urls = yaml.safe_load(file)

def check_user():
    response = requests.post(api_urls['CHECK_USER_URL'],json={'username':'test_user'})
    assert response.status_code == 200
    response = response.json()
    st.session_state['username'] = response['username']
    st.session_state['threads'] = response['threads']
    st.session_state['thread_id'] = ' '
    st.session_state['messages'] = []

def new_chat():
    response = requests.post(api_urls['NEW_CHAT_URL'],json={'username':'test_user'})
    assert response.status_code == 200
    response = response.json()
    st.session_state['username'] = response['username']
    st.session_state['threads'] = response['threads']
    st.session_state['thread_id'] = response['thread_id']
    st.session_state['messages'] = []

def get_chat():
    thread_id = st.session_state['Chats']
    st.session_state.thread_id = thread_id
    response = requests.post(api_urls['GET_CHAT_URL'],json={
        'username':st.session_state.username,
        'thread_id':st.session_state.thread_id
    })
    assert response.status_code == 200
    response = response.json()
    if response['messages']==None:
        st.session_state['messages'] = []
    else:
        st.session_state['messages'] = response['messages']

# Streamlit app layout
def main():

    if 'username' not in st.session_state:
        check_user()
        # st.session_state['cost'] = dict().fromkeys(['tokens','dollar','prompt_length','response_length'])

    with st.sidebar:
        st.selectbox('Chats',options=[k for k in st.session_state.threads.keys()],key='Chats')
        cols = st.columns([0.2,0.3,0.3,0.2])
        with cols[1]:
            with st.form('Select Chat',border=False):
                st.form_submit_button('Switch Chat',on_click=get_chat)
        with cols[2]:
            with st.form('Sidebar New Chat',border=False):
                st.form_submit_button('New Chat',on_click=new_chat)
    
    if st.session_state.thread_id == ' ':
        st.container(height=400,border=False)
        cols = st.columns([0.33]*3)
        with cols[1]:
            with st.form('New Chat',border=False):
                st.form_submit_button('New Chat',on_click=new_chat)
    else:
        if chat_input:=st.chat_input('Hello, how do you want me to help you today?'):
            response = requests.post(api_urls['CHAT_URL'],json={
                'username':st.session_state['username'],
                'thread_id':st.session_state['thread_id'],
                'message':chat_input
            })
            assert response.status_code == 200
            response = response.json()
            st.session_state.messages = response['messages']
        if len(st.session_state.messages)!=0:
            for message in st.session_state.messages:
                with st.chat_message(message['role']):
                    st.write(message['content'])


if __name__ == "__main__":
    main()
