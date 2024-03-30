import os
import time
import json
import yaml
import datetime
import pandas as pd
import json


from flask import Flask,request,jsonify
from flask_sock import Sock
from openai import OpenAI
from symbol_pair import pairs,supported_indicators

import pymongo
from pymongo import MongoClient


with open("strategy_params.yml", "r") as file:
  # Read the file contents
  strategy_params = yaml.safe_load(file)

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
sock = Sock(app)
client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))
return_message = None

assistant = client.beta.assistants.create(
    name="strategy_generator",
    instructions=f"""
        You are FormaxionBot, an assistant on the Formaxion website that helps trader in generating strategies for stock trading on Nigerian stock Exchange (NGX).
        Formaxion is a cutting-edge web platform revolutionizing the Nigerian stock trading landscape. Tailored for both seasoned investors and newcomers, 
        traders can create strategies using drag and drop or prompt you to create strategy for them. the generated strategy will be sent to the backtesting engine 
        for analysis so the strategy you generate must always be in json format. The currently supported indicators are current price, 
        exponential moving average of price, moving average of price,  relative strength index, standard deviation of price. There will be support for other indicators in the 
        future.The building blocks of the strategies are asset, weight, conditional, filter which has its corresponding json representation. 

        {pairs} is the company name and symbol pairing for stocks listed on the Nigerian Stock Exchange (NGX) . 

        asset = {{
            "type":"asset",
            "symbol":"UBA"    
        }}

        weight = {{
            "weight": "weight-specified", 
            "blocks":[ ]
        }}

        options for weight  ["weight-equal", "weight-specified"]. must be 2 decimal places and sum must be equal to 1.

        conditional = ((
            "type": "conditional",
            "condition": (
                "subject": (
                    "function":"moving-average-price", 
                    "asset":"UBA", 
                    "period": "1", 
                    ),
                "comparison": "greater-than", 
                "predicate": (
                    "type":"function", #options: ["function", "value"] 
                    "function":"moving-average-price",
                    "period": "1", #days
                    "asset":"UBA",
                    
                    )
                ),
            "then": [
                        (
                    "type":"asset",
                    "symbol":"UBA"    
                    )
                ],
            "else": [
                (
                    "type":"asset",
                    "symbol":"ZENITHBANK"    
                )
                ],
        ))
        option for function is ["current_price", "moving-average-price","relative-strength-index","exponential-moving-average-price","standard-deviation-price"]
        option for comparison is ["greater-than", "less-than"]
        filter = ((
            "type": "filter",
            "sort":()
                "function":"moving-average-price",
                "period": "1",
                ),
            "select":["top, 5"], #options: ["top, 5", "bottom, 5"] number could between 5 to 15
            ))

        example of stratgey using above blocks is strategy = ((
            "name": "test1",
            "description": "test1",
            "rebalance_frequency": "weekly",
            "weight": (
                "type":"weight-specified",
                "blocks":[
                    (
                    "value":0.65,
                    "type":"asset",
                    "symbol":"UBA"  
                    ),
                    (
                        "value":0.35,
                        "type": "conditional",
                            "condition": ((
                                "subject": (
                                    "function":"moving-average-price",
                                    "asset":"UBA",
                                    "period": "1",
                                    ),
                                "comparison": "greater-than",
                                "predicate": (
                                    "type":"function",
                                    "function":"moving-average-price",
                                    "asset":"ZENITHBANK",
                                    "period": "1",
                                    )
                                )),
                            "then": [
                                        (
                                    "type":"asset",
                                    "symbol":"ZENITHBANK"    
                                    )
                                ],
                            "else": [
                                (
                                    "type":"asset",
                                    "symbol":"CONOIL"    
                                )
                            ],
                    )
                ]
            )

    """,
    model="gpt-3.5-turbo-1106")

threads = dict()

@sock.route("/")
def fresh(ws):
    data = ws.receive()
    ws.send(json.dumps({"data": {
        "message": "Request processed successfully. You can start prompting"
    }}))

@sock.route("/check_user")
def check_user(ws):

    data = json.loads(ws.receive())
    print(data)
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

    ws.send(json.dumps({
        "username":user,
        "threads":json.dumps(user_threads_)
    }))

@sock.route("/get_chat")
def get_chat(ws):

    data = json.loads(ws.receive())
    # data = request.get_json()
    user = data.get("username")
    thread_id = data.get("thread_id")

    user_ = collection.find_one({"user": user})
    if user_:
        user_threads_ = user_.get("threads")
        messages = user_threads_[thread_id]["messages"]
        tokens = user_threads_[thread_id]["tokens"]
        ws.send(json.dumps({
            "username":user,
            "thread_id":thread_id,
            "messages":json.dumps(messages),
            "tokens":tokens
        }))
    else:
        error_response = {
            "error": "Bad Request",
            "message": "User not found in database"
        }
        ws.send(json.dumps([error_response,400]))


@sock.route("/new_chat")
def create_chat(ws):

    data = json.loads(ws.receive())
    user = data.get("username")

    user_ = collection.find_one({"user": user})
    if user_:
        thread = client.beta.threads.create()
        user_threads_ = user_.get("threads")
        if user_threads_:
            user_threads_[thread.id]=dict().fromkeys(["name","messages","time","tokens"])
        else:
            user_threads_ = {thread.id:dict().fromkeys(["name","messages","time","tokens"])}
        collection.update_one(
                {"user": user},
                {"$set": {"threads": user_threads_}}
            )

    ws.send(json.dumps({
        "username":user,
        "threads":json.dumps(user_threads_),
        "thread_id":thread.id
    }))
    

@sock.route("/chat")
def chat(ws):
    data = json.loads(ws.receive())
    user = data.get("username")
    thread_id = data.get("thread_id")
    message = data.get("message")

    user_ = collection.find_one({"user": user})
    if user_:
        user_threads_ = user_.get("threads")
        if thread_id not in user_threads_:
            error_response = {
                "error": "Bad Request",
                "message": "Selected chat does not exist for current user"
            }
            return jsonify(error_response), 400
        else:
            message = client.beta.threads.messages.create(
                thread_id = thread_id,
                role = "user",
                content = message
            )
            run = client.beta.threads.runs.create(
                thread_id = thread_id,
                assistant_id = assistant.id,
            )
            while run.status in ["queued", "in_progress", "cancelling"]:
                time.sleep(1) # Wait for 1 second
                run = client.beta.threads.runs.retrieve(
                    thread_id = thread_id,
                    run_id = run.id
                )
            if run.status == "completed": 
                messages = client.beta.threads.messages.list(
                    thread_id = thread_id
                )
                messages.data.reverse()
                return_messages = []
                for thread_message in messages.data:
                    message = client.beta.threads.messages.retrieve(
                        thread_id = thread_id,
                        message_id = thread_message.id
                    )
                    return_messages.append({
                        "role":message.role,
                        "content":message.content[0].text.value,
                    })
    else:
        error_response = {
            "error": "Bad Request",
            "message": "user should be created with /new_chat endpoint"
        }
        return jsonify(error_response), 400
    
    # update database thread_id with return_messages
    user_threads_[thread_id]["messages"] = return_messages
    if user_threads_[thread_id]["tokens"] == None:
        user_threads_[thread_id]["tokens"] = []
    user_threads_[thread_id]["tokens"].append(run.usage.prompt_tokens)
    user_threads_[thread_id]["tokens"].append(run.usage.completion_tokens)
    user_threads_[thread_id]["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    collection.update_one(
            {"user": user},
            {"$set": {"threads": user_threads_}}
        )

    ws.send(json.dumps({
        "username":user,
        "thread_id":thread_id,
        "messages":json.dumps(return_messages),
        "tokens":user_threads_[thread_id]["tokens"]
    }))

"""ADMIN ENDPOINTS"""

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
    app.run(debug=True)