import streamlit as st
import requests
import time

# Define a function to generate responses based on user input
def get_strategy(prompt):
    payload = {
        'username':st.session_state.username,
        'message':prompt,
        'history':st.session_state.chats
    }
    print('running')
    # response = requests.post('https://formaxion-ai.onrender.com/strategize',json=payload)
    response = requests.post('http://127.0.0.1:5000/strategize',json=payload)
    print('response received')
    if response.status_code == 200:
        response = response.json()
        st.session_state.chats.append({
            'role':'assistant',
            'content':response['strategy']
        })
    else:
        print(response)

# Streamlit app layout
def main():
    if 'chats' not in st.session_state:
        st.session_state['chats'] = []

    if 'username' not in st.session_state:
        st.session_state['username'] = 'test_user'

    print(st.session_state.username)

    st.title("Test formaxionAI")

    # Check if the user has entered a message
    if chat_input:=st.chat_input('What Strategy are you looking for'):
        st.session_state.chats.append({
            'role':'user',
            'content':chat_input
        })
        print('prompt entered')
        get_strategy(chat_input)
        for i in range(len(st.session_state.chats)):
            if st.session_state.chats[i]['role']=='user':
                with st.chat_message('user'):
                    st.write(st.session_state.chats[i]['content'])
            elif st.session_state.chats[i]['role']=='assistant':
                with st.chat_message('assistant'):
                    st.write(st.session_state.chats[i]['content'])


if __name__ == "__main__":
    main()
