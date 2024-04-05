import os
import time
import json
import yaml
import datetime
import pandas as pd
import json


from flask import Flask,request,jsonify
# from flask_sock import Sock
from flask_socketio import SocketIO, emit
from openai import OpenAI
from .assistant_parameters import assistant_instructions

import pymongo
from pymongo import MongoClient

print("Attempting MongoDB connection.................")
cluster = MongoClient(os.environ.get("MONGO_URL"))
try:
    cluster.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    exit()
time.sleep(3)
db = cluster["formaxion"]
collection = db["users_threads"]
db_connect = True

app = Flask(__name__)
# sock = Sock(app)
app.config["SECRET_KEY"] = "ABCDFRHGRPTY"
socketio = SocketIO(app,cors_allowed_origins="*")
client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))
return_message = None

assistant = client.beta.assistants.retrieve(os.environ.get("ASSISTANT_ID"))
print(f"Asssistant ID: {assistant.id}")



"""REST ENDPOINTS"""
@app.route("/check_user",methods=["POST"])
def check_user():

    data = request.get_json()
    user = data.get("username")

    user_ = collection.find_one({"user": user})
    if user_:
        user_threads_ = user_.get("threads")
    else:
        user_threads_ = {}
        new_user = {
            "user": user,
            "threads": user_threads_
        }
        collection.insert_one(new_user)

    return json.dumps({
        "username":user,
        "threads":list(user_threads_.keys())
    })

@app.route("/chat/<username>/<thread_id>/get_chat",methods=["GET"])
def get_chat(username, thread_id):

    user_ = collection.find_one({"user": username})
    if user_:
        user_threads_ = user_.get("threads")
        messages = user_threads_[thread_id]["messages"]
        tokens = user_threads_[thread_id]["tokens"]
        return jsonify({
            "username":username,
            "thread_id":thread_id,
            "messages":messages,
            "tokens":tokens
        })
    else:
        error_response = {
            "error": "Bad Request",
            "message": "User not found in database"
        }
        return jsonify(error_response), 400


@app.route("/chat/<username>/new_chat",methods=["GET"])
def create_chat(username):

    user_ = collection.find_one({"user": username})
    if user_:
        thread = client.beta.threads.create()
        user_threads_ = user_.get("threads")
        if user_threads_:
            user_threads_[thread.id]=dict().fromkeys(["name","messages","time","tokens"])
        else:
            user_threads_ = {thread.id:dict().fromkeys(["name","messages","time","tokens"])}
        collection.update_one(
                {"user": username},
                {"$set": {"threads": user_threads_}}
            )

        return jsonify({
            "username":username,
            "thread_id":thread.id,
            "name":user_threads_[thread.id]["name"]
        })



"""WEB SOCKET CONNECTIONS"""
@socketio.on("connect")
def handle_connect():
    print("connected")

@socketio.on("diconnect")
def handle_disconnect():
    print("disconnected")

@socketio.on("chat")
def chat(message):
    user = message.get("username")
    thread_id = message.get("thread_id")
    message_ = message.get("message")
    user_threads_ = ping_assistant(user=user,thread_id=thread_id, message_=message_)
    response_message = json.dumps({
        "username":user,
        "thread_id":thread_id,
        "messages":user_threads_[thread_id]["messages"][-1]["content"],
        "tokens":user_threads_[thread_id]["tokens"][-2:]
    })
    emit("chat_return",response_message)
    print("Emitted")
    del user,thread_id,message_,user_threads_,response_message

@socketio.on("message")
def message(msg):
    user="test_user"
    thread_id="thread_xFAEVZO3i2ver7ouQN7ykuBD"
    message_ = msg
    user_threads_ = ping_assistant(user=user, thread_id=thread_id,message_=message_)
    message_ = json.dumps({
        "messages":user_threads_[thread_id]["messages"][-1]["content"],
        "thread_id":thread_id,
        "tokens":user_threads_[thread_id]["tokens"][-1]
    })
    emit("message",message_)
    del user,thread_id,message_,user_threads_

def ping_assistant(user, thread_id, message_):
    user_ = collection.find_one({"user": user})
    if user_:
        user_threads_ = user_.get("threads")
        if thread_id not in user_threads_:
            error_response = {
                "error": "Bad Request",
                "message": "Selected chat does not exist for current user"
            }
            error_response = json.dumps([error_response,400])
            emit("error",error_response)
            return
        else:
            message_ = client.beta.threads.messages.create(
                thread_id = thread_id,
                role = "user",
                content = message_
            )
            run = client.beta.threads.runs.create(
                thread_id = thread_id,
                assistant_id = assistant.id,
            )
            print("---------------------------")
            print(f"run start time: {time.time()}")
            while run.status in ["queued", "in_progress", "cancelling"]:
                # time.sleep(0.005) # Wait for 1 second
                run = client.beta.threads.runs.retrieve(
                    thread_id = thread_id,
                    run_id = run.id
                )
            print(f"run stop time: {time.time()}")
            if run.status == "completed":
                if user_threads_[thread_id]["messages"]==None:
                    user_threads_[thread_id]["messages"] = []
                print(f"run completion time: {time.time()}") 
                messages = client.beta.threads.messages.list(
                    thread_id = thread_id
                )
                print(type(messages.data[0].role),messages.data[0].content[0].text.value)
                print(type(messages.data[1].role),messages.data[1].content[0].text.value)
                for i in [1,0]:
                    user_threads_[thread_id]["messages"].append({
                        "role":messages.data[i].role,
                        "content":messages.data[i].content[0].text.value
                    })
            print(f"message processing time: {time.time()}")
    else:
        error_response = {
            "error": "Bad Request",
            "message": "user should be created with /new_chat endpoint"
        }
        error_response = json.dumps([error_response,400])
        emit("error",error_response)
        return
    
    if user_threads_[thread_id]["tokens"] == None:
        user_threads_[thread_id]["tokens"] = []
    user_threads_[thread_id]["tokens"].append(run.usage.prompt_tokens)
    user_threads_[thread_id]["tokens"].append(run.usage.completion_tokens)
    user_threads_[thread_id]["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    collection.update_one(
            {"user": user},
            {"$set": {"threads": user_threads_}}
        )
    
    return user_threads_


"""ADMIN REST ENDPOINTS"""
@app.route("/admin/tokens_history",methods=["GET"])
def tokens_history():
    df = []
    cursor = collection.find({},{"threads":1})
    for document in cursor:
        for thread in document["threads"]:
            item_ = {
                "time":datetime.datetime.strptime(document["threads"][thread]["time"], "%Y-%m-%d %H:%M:%S"),
                "tokens":sum(document["threads"][thread]["tokens"])
                }
            df.append(item_)
    return jsonify({
        "tokens_times":df
    })



if __name__=="__main__":
    socketio.run(app)