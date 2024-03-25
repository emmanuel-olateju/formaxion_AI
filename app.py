import os
import json
from flask import Flask,request,jsonify
import openai

app = Flask(__name__)

openai.api_key = os.environ.get('OPENAI_KEY')

global AI_Agent_description
AI_agent_description = '''
    Hi, I am Asakoro.
    I am your trading assistant developed to help you generate strategies for optimizing your return on investement in the African stock exchange market.
    Here is a list of what I can do:
        1. Generate algorithm for trading strategies
        2. Explain trading concepts to you
        3. Provide recent data on the African stock exchange market
        4. Provide statistics on common winning strategies in the African stock market
    Here is how I work, tell me what stocks you are interested in and I would generate strategies for you. You could also tell me what trading or stock exchange market 
    concept you are struggling with and I would do my best to explain it to you at a granular level. You could request statistics on trends in the African stock 
    exchange market or you could ask me for winning strategies for prticular stocks.
'''


def personality_prompt_template(prompt,chat_history):
    global AI_agent_description
    prompt_template = f"""
    Note the following:
        1. The PROMPT given is delimited using xml tags.
        2. The CHAT_HISTORY is delimited using triple dashes.
        3. The CHAT_HISTORY is a tuple of two elements.
            a. The first element is a list of dictionaries with keys role and content, where the content is a past PROMPT from the user.
            b. The second element is a list of dictionaries with keys role and content, where the content is one of your past response to the \
            appropriate index of PROMPT input in the first tuple element.

        SCAN through the CHAT_HISTORY
        IF you have described youself anywhere in the CHAT_HISTORY to the user
            Proceed with the next actions, witin the context of your past responses, also reminding the user you have described yourself previously

        IF the PROMPT is not about stock trading,
        Forget your past response about the AI agent or your past response to any greetings
            IF the PROMPT is not asking about you the AI agent AND it is not a greeting or salutation,
                generate a polite response explaining the following:
                    1. You are an AI assistant and adviser for stock trading in the African stock exchange market
                    2. You cannot provide answers to questions outside African stocks trading
                    3. You would need user input about the african stock market or taking actions as a trader in the african stock market
            ELSE:
                IF you find a greeting within the PROMPT:
                    respond with a polite greeting also and then concisely describe yourself based on this description {AI_agent_description}
                ELSE:
                    explicitly describe yourself based on this description {AI_agent_description}

        PROMPT: <tag>{prompt}</tag>
        CHAT_HISTORY: ---{chat_history}---
    """
    return prompt_template

def generate_strategy(prompt):
    response = openai.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages = [{
            'role':'user',
            'content':prompt
        }]
    )
    return response.choices[0].message.content

strategies = None

@app.route('/')
def fresh():
    return jsonify({
    "data": {
        "message": "Request processed successfully. You can start prompting"
    }
})

@app.route('/strategize',methods=['POST'])
def chat():
    data = request.get_json()
    user = data.get('username')
    message = data.get('message')
    history = data.get('history')
    strategies = {'message':[],'strategy':[],'code':[]}
    strategies['message'].append({
        'role':'user',
        'content':message
    })
    '''PERSONALITY TEST'''
    generated_strategy = generate_strategy(personality_prompt_template(message,history))
    # print(' ')
    # print(' ')
    # print(' ')
    # print(' ')
    # print(f'strategy:{generated_strategy}')
    # prompt = f'{message}. Speak in pseudocode and explain pros and cons in plain English to a teenager'
    # Generate Strategy in pseudocode and save in strategy chat_history object
    # generated_strategy = generate_strategy([{'role':'user','content':prompt}])
    # strategies['strategy'].append({
    #     'role':'assistant',
    #     'content':generated_strategy
    # })
    # # Generate pseudocode of strategy
    # pseudocode = generate_strategy([{
    #     'role':'assistant',
    #     'content':f'extract the pseudocode from this strategy explained as thus:{generated_strategy}'
    # }])
    # strategies['code'].append({
    #     'role':'assistant',
    #     'content':pseudocode
    # })
    return jsonify({
        'message':message,
        'strategy':generated_strategy,
        'code':''
    })

if __name__=='__main__':
    app.run(debug=True)