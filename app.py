import os
import json
from flask import Flask,request,jsonify
import openai

app = Flask(__name__)

openai.api_key = os.environ.get('OPENAI_KEY')
def generate_strategy(prompt):
    response = openai.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages = prompt
    )
    return response.choices[0].message.content

strategies = None

@app.route('/')
def fresh():
    global strategies
    if strategies is None:
        strategies = {'message':[],'strategy':[],'code':[]}
    return strategies

@app.route('/strategize',methods=['POST'])
def chat():
    data = request.get_json()
    user = data.get('username')
    message = data.get('message')
    global strategies
    if strategies is None:
        strategies = {'message':[],'prompt':[],'strategy':[],'code':[]}
    strategies['message'].append({
        'role':'user',
        'content':message
    })
    # IMPLEMENT MORE ADVANCED PROMPTING
    prompt = f'{message}. Speak in pseudocode and explain pros and cons in plain English to a teenager'
    # Generate Strategy in pseudocode and save in strategy chat_history object
    generated_strategy = generate_strategy([{'role':'user','content':prompt}])
    strategies['strategy'].append({
        'role':'assistant',
        'content':generated_strategy
    })
    # Generate pseudocode of strategy
    pseudocode = generate_strategy([{
        'role':'assistant',
        'content':f'extract the pseudocode from this strategy explained as thus:{generated_strategy}'
    }])
    strategies['code'].append({
        'role':'assistant',
        'content':pseudocode
    })
    return jsonify({
        'message':message,
        'strategy':generated_strategy,
        'code':pseudocode
    })

if __name__=='__main__':
    app.run(debug=True)