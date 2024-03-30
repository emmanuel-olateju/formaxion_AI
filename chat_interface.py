import streamlit as st
import requests
import copy

import os
import json
import yaml

import asyncio
import websockets



async def check_user():
    async with websockets.connect(os.environ.get("CHECK_USER_URL")) as ws:
        await ws.send(json.dumps({"username":"test_user"}))
        response = await ws.recv()
        response = json.loads(response)
        st.session_state["username"] = response["username"]
        st.session_state["threads"] = json.loads(response["threads"])
        st.session_state["thread_id"] = " "
        st.session_state["messages"] = []
        st.session_state["tokens"] = []

async def new_chat():
    async with websockets.connect(os.environ.get("NEW_CHAT_URL")) as ws:
        await ws.send(json.dumps({"username":"test_user"}))
        response = await ws.recv()
        response = json.loads(response)
        st.session_state["username"] = response["username"]
        st.session_state["threads"] = json.loads(response["threads"])
        st.session_state["thread_id"] = response["thread_id"]
        st.session_state["messages"] = []
        st.session_state["tokens"] = []

def new_chat_():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(new_chat())

async def get_chat():
    thread_id = st.session_state["Chats"]
    st.session_state.thread_id = thread_id
    async with websockets.connect(os.environ.get("GET_CHAT_URL")) as ws:
        await ws.send(json.dumps({"username":st.session_state.username,"thread_id":st.session_state.thread_id}))
        response = await ws.recv()
        response = json.loads(response)
        st.session_state["messages"] = json.loads(response["messages"])
        st.session_state["tokens"] = response["tokens"]

def get_chat_():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_chat())


async def chat(chat_input):
    async with websockets.connect(os.environ.get("CHAT_URL")) as ws:
        await ws.send(json.dumps({"username":st.session_state["username"],"thread_id":st.session_state["thread_id"],"message":chat_input}))
        response = await ws.recv()
        response = json.loads(response)
        return response

# Streamlit app layout
async def main():
    # new_chat_ = lambda: asyncio.run_coroutine_threadsafe(new_chat(),asyncio.get_running_loop())

    if "username" not in st.session_state:
        await check_user()

    with st.sidebar:
        st.selectbox("Chats",options=[k for k in st.session_state.threads.keys()],key="Chats")
        cols = st.columns([0.2,0.3,0.3,0.2])
        with cols[1]:
            with st.form("Select Chat",border=False):
                st.form_submit_button("Switch Chat",on_click=get_chat_)
        with cols[2]:
            with st.form("Sidebar New Chat",border=False):
                st.form_submit_button("New Chat",on_click=new_chat_)
    
    if st.session_state.thread_id == " ":
        st.container(height=400,border=False)
        cols = st.columns([0.33]*3)
        with cols[1]:
            with st.form("New Chat",border=False):
                st.form_submit_button("New Chat",on_click=new_chat_)
    else:
        if chat_input:=st.chat_input("Hello, how do you want me to help you today?"):
            response = await chat(chat_input=chat_input)
            st.session_state.messages = json.loads(response["messages"])
            st.session_state.tokens = response["tokens"]
        if len(st.session_state.messages)!=0:
            for m,message in enumerate(st.session_state.messages):
                cols = st.columns([0.8,0.2])
                with cols[0]:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                with cols[1]:
                    # print(st.session_state.tokens)
                    st.write("Tokens: {}".format(st.session_state.tokens[m]))
            with st.sidebar:
                st.write("Total Tokens: {}".format(sum(st.session_state.tokens)))


if __name__ == "__main__":
    asyncio.run(main())

