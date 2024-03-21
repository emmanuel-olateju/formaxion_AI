import requests

strategize_url = 'https://formaxion-ai.onrender.com/strategize'

strategize_payload = {
    'username':'test_user',
    'message':'Develop a RSI strategy for QQQ'
}

def test_strategize():
    response = requests.post(strategize_url,json=strategize_payload)
    if response.status_code == 200:
        return response.json()
    else:
        return response
    
if __name__ == '__main__':
    res = test_strategize()
    print(res)