import os
import time
import json
import yaml


from flask import Flask,request,jsonify
from openai import OpenAI
from symbol_pair import pairs,supported_indicators

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get('OPENAI_KEY'))
return_message = None

with open("strategy_params.yml", 'r') as file:
  # Read the file contents
  strategy_params = yaml.safe_load(file)

assistant = client.beta.assistants.create(
    name='strategy_generator',
    instructions=f'''
        You are FormaxionBot, an assistant on the Formaxion website that helps trader in generating strategies for stock trading on Nigerian stock Exchange (NGX).
        Formaxion is a cutting-edge web platform revolutionizing the Nigerian stock trading landscape. Tailored for both seasoned investors and newcomers, 
        traders can create strategies using drag and drop or prompt you to create strategy for them. the generated strategy will be sent backtesting engine 
        for analysis so the strategy you generate must always be in json format. the currently supported indicators are current price, 
        exponential moving average of price, moving average of price,  relative strength index, standard deviation of price. there will be support for other indicators in the future.
        the building blocks of the strategies are asset, weight, conditional, filter which has its corresponding json representation. 

        {pairs}is the company name and symbol pairing for stocks listed on the Nigerian Stock Exchange (NGX) . 

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

    ''',
    model='gpt-3.5-turbo-1106')

threads = dict()

@app.route('/')
def fresh():
    return jsonify({
    "data": {
        "message": "Request processed successfully. You can start prompting"
    }
})

@app.route('/new_chat',methods=['POST'])
def create_chat():
    data = request.get_json()
    user = data.get('username')

    thread = client.beta.threads.create()
    if user not in threads:
        threads[user] = dict()
    threads[user][thread.id] = thread

    return jsonify({
        'username':user,
        'thread_id':thread.id
    })
    

@app.route('/chat',methods=['POST'])
def chat():
    data = request.get_json()
    user = data.get('username')
    thread_id = data.get('thread_id')
    message = data.get('message')

    if user not in threads:
        error_response = {
            'error': 'Bad Request',
            'message': 'user should be created with /new_chat endpoint'
        }
        return jsonify(error_response), 400
    elif thread_id not in threads[user]:
        error_response = {
            'error': 'Bad Request',
            'message': 'Selected chat does not exist for current user'
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
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1) # Wait for 1 second
            run = client.beta.threads.runs.retrieve(
                thread_id = thread_id,
                run_id = run.id
            )
        if run.status == 'completed': 
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
                    'role':message.role,
                    'content':message.content[0].text.value
                })

   
    return jsonify({
        'username':user,
        'thread_id':thread_id,
        'messages':return_messages
    })

if __name__=='__main__':
    app.run(debug=True)