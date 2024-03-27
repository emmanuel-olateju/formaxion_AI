import os
import time
import json
from flask import Flask,request,jsonify
from openai import OpenAI
from symbol_pair import pairs,supported_indicators

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get('OPENAI_KEY'))
return_message = None

assistant = client.beta.assistants.create(
    name='strategy_generator',
    instructions=f'''
        You are an assistant to help generate strategies for trading the following {pairs} in the Nigerian stock exchange market
        Your can generated strategies using just the following supported indicators: {supported_indicators}.
        Your are only allowed to discuss topics around Nigerian stock trading and generate strategies for Nigerian stocks.
        When you are asked to generatie a strategy, your output should only be a python code of the strategy.
        Do not make use of non builtin python packages in your strategy codes.
        You are allowed to discuss stocks outside Nigeria and generate strategies for them if you have prior information on them.
    ''',
    model='gpt-3.5-turbo')

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