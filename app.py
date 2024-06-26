import os
import json
from flask import Flask,request,jsonify
import openai

app = Flask(__name__)

openai.api_key = os.environ.get('OPENAI_KEY')

global context
context = [{
    'user':'system',
    'content': f'''
    You are a system to assist in trading strategies within the Nigerian stock market,
    your operations do not allow you to perform in the context of trading non Nigerian stocks,
    your operations also do not allow you to do do any other thing apart from generating strategies
    and algorithms that can improve or aid trading in the Nigerian stock market.
    All of your responses apart from Yes/No responses should be in form of direct speech with the user using the first person language.
    Your prompts will also involve conditionals indicated by IF and ELSE which serve as aguide for the construct of your repsonses based on scenarios.
    The description of the construct of yout response will be indented under the conditionals and should only be executed after checking the conditions in brackets.
    The response construct under conditionals will be delimited by double dashes. ELSE will not have conditions in brackets but will contain response constructs indented
    below.
    '''
}]

global AI_Agent_description
AI_agent_description = '''
    Hi, I am Asakoro.
    I am your trading assistant developed to help you generate strategies for optimizing your return on investement in the Nigerian stock exchange market.
'''

def rules_template(rules):
    global context
    return f'Basic rules you should abide by to generate your response are described as follows: {rules}'

def personality_prompt_template(prompt):
    prompt_template = rules_template(context[0]['content'])+f"""
    If the input which is delimited by xml tags asks questions about your identity, capabilities, functions, or the input is a greeting or salutation, then \
    you respond with a similar greeting describing your capabilities and functionalities based on the basic rules you are to abide by in generating responses. \
    If in your chat history you have described your identity or functionalities before, in your response remind the user that you have \
    described your functions before. But if the input does not meet any of the criteria stated respond with a simple yes.

    INPUT: <tag>{prompt}</tag>
    """
    return prompt_template

def strategy_generation_template(prompt):
    global AI_agent_description, context
    prompt_template = rules_template(context[0]['content'])+f"""
    If the input delimited by xml tags is requesting for the generation of a strategy for an institution or for particular kind of stocks. \
    Check if the institution, or stocks the user is requesting a strategy for operates within Nigeria. \
    If the institution or stock can be found in the Nigerian stock market, then generate a strategy as requested by the user. \
    If the stock cannot be found within the Nigerian stock market, generate a strategy for any example stock you can find \
    Your output should contain three things, one a pseudocode implementation of the strategy, then the implementation of the strategy in python and an explaination \
    of the strategy.

    INPUT: <tag>{prompt}</tag>
    """

    return prompt_template

def generate_strategy(prompt):
    if isinstance(prompt,str):
        msg = [{
            'role':'user',
            'content':prompt
        }]
    elif isinstance(prompt,list):
        msg = prompt
    response = openai.chat.completions.create(
        model = 'gpt-3.5-turbo-0125',
        messages = msg,
        temperature=0.5
    )
    return response.choices[0].message.content


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
    assert isinstance(history,list)
    assert history[-1]['role']=='user'

    '''PERSONALITY TEST'''
    generated_strategy = generate_strategy(personality_prompt_template(message))
    if 'yes' in generated_strategy.lower():
        prompt = strategy_generation_template(message)
        history[-1]['content'] = prompt
        generated_strategy = generate_strategy(history[-1]['content'])
   
    return jsonify({
        'strategy':generated_strategy,
        'code':''
    })

if __name__=='__main__':
    app.run(debug=True)