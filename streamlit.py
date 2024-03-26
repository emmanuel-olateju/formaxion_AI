import streamlit as st
import requests
import time
import copy

import os
import json
from openai import OpenAI

from symbol_pair import pairs

with open('stocks.json', "r") as json_file:
    stocks = json.load(json_file)

client = OpenAI(api_key=st.secrets['OPENAI_KEY'])

def create_message(prompt):
    st.session_state.messages = client.beta.threads.messages.create(
        thread_id = st.session_state.thread.id,
        role="user",
        content=prompt
    )

# Streamlit app layout
def main():

    st.title("Test formaxionAI")

    if 'username' not in st.session_state:
        st.session_state['username'] = "test_user"
    if 'assistant' not in st.session_state:
        st.session_state['assistant'] = client.beta.assistants.create(
            name='strategy_generator',
            instructions=f'''
                You are an assistant to help generate strategies for trading the following {pairs} in the Nigerian stock exchange market. \
                Your are limited to making use of either the RSI or momentum strategies. \
                Your are only allowed to discuss topics around Nigerian stock trading and generate strategies for Nigerian stocks. \
                When you are generating strategies for any stock, your output should simply be a python code of the strategy
            ''',
            model='gpt-3.5-turbo-0125'
        )
    if 'thread' not in st.session_state:
        st.session_state['thread'] = client.beta.threads.create()
    if 'messages' not in st.session_state:
        st.session_state['messages'] = None

    # Check if the user has entered a message
    if chat_input:=st.chat_input('What Strategy are you looking for'):
        create_message(chat_input)
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread.id,
            assistant_id=st.session_state.assistant.id,
            )
  
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1) # Wait for 1 second
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread.id,
                run_id=run.id
            )
        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread.id
            )
            messages.data.reverse()
            for thread_message in messages.data:
                message = client.beta.threads.messages.retrieve(
                    thread_id=st.session_state.thread.id,
                    message_id=thread_message.id
                )
                with st.chat_message(message.role):
                    st.write(message.content[0].text.value)
                print(type(messages.data[0]),message.content[0].text.value)
        else:
            print(run.status)


if __name__ == "__main__":
    main()
