import os
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
import json
from openai import OpenAI
import logging
from dotenv import load_dotenv

from config.config import Config

load_dotenv()
config = Config('deepseek-chat')

# Initialize logging to console - do not use file appenders in container mode
logging.basicConfig(level=config.get('LOG_LEVEL', default= 'INFO'), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info('STARTING model.py')

LIEV_PASSWORD = config.get("LIEV_PASSWORD")
LIEV_USERNAME = config.get("LIEV_USERNAME")

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

def transform_messages(messages):
    # Para manter o padrão da openai é necessário fazer uma transformação nas mensagens
    # O gpt-4 e alguns anteriores são multimodels, que podem executar diversas ações, além de gerar textos
    # O deepseek não é um multimodel, então não deve-se passar a tag "type"

    # Função para verificar se a lista já está no formato transformado
    def is_transformed(messages):
        # Verifica se 'content' em cada mensagem é uma string, o que indica o novo formato
        return all(isinstance(message['content'], str) for message in messages)

    # Lista transformada
    transformed_messages = []

    # Verifica se a lista já está transformada
    if is_transformed(messages):
        transformed_messages = messages
    else:
        # Loop para transformar cada mensagem
        for message in messages:
            # Verifica se a 'content' é uma string; se sim, pega diretamente
            if isinstance(message['content'], str):
                text = message['content']
            # Caso contrário, acessa o texto que está dentro de uma lista de dicionários
            else:
                text = message['content'][0]['text']
            # Cria um novo dicionário com a estrutura desejada e adiciona à lista transformada
            transformed_messages.append({'role': message['role'], 'content': text})

    # Retorna o resultado
    return transformed_messages

@auth.verify_password
def verify(username, password):
    """ Verify: Check username and password to allow access to the API"""
    if not (username and password):
        return False
    return username == LIEV_USERNAME and password == LIEV_PASSWORD


@app.route('/response')
@auth.login_required
def response():
    #Init Deepseek
    DEEPSEEKAPIKEY=config.get('DEEPSEEKAPIKEY')
    MODEL=config.get('MODEL', 'deepseek-chat')
    BASE_URL= config.get('BASE_URL', 'https://api.deepseek.com')
    client = OpenAI(api_key=DEEPSEEKAPIKEY, base_url=BASE_URL)


    data = request.data
    try:
        data = json.loads(data)
    except Exception as e:
        logger.error(f"JSON load problem!: {e}", exc_info=True)
        return json.dumps("JSON load problem !"), 500

    if isinstance(data, dict) == False:
        return json.dumps("JSON load conversion problem. Not a dict ! Are you using data payload  ?"), 400
    
    stream              = False
    max_tokens          = int(data.get('max_tokens',4096))
    frequency_penalty   = float(data.get('frequency_penalty',0))
    presence_penalty    = float(data.get('presence_penalty',0))
    stop_words          = data.get('stop', [])
    temperature         = float(data.get('temperature', 1))
    logprobs            = bool(data.get('logprobs',False))
    top_logprobs        = data.get('top_logprobs',None)
    top_p               = float(data.get('top_p', 1))

    # verifica se existe a chave messages no dict:
    if data.get('messages'):
        # se existir, verifica se existe instruction ou system_msg juntos
        if data.get('instruction') or data.get('system_msg'):
            return json.dumps("If the messages parameter is passed, the instruction or system_msg parameters must not be passed."), 501
        messages = data['messages']
        messages = transform_messages(messages)
    else:
        instruction = data.get('instruction', "hi")
        system_msg = data.get('system_msg', None)
        history = data.get('history', [])

        messages = []
        for h in history:
            messages.append({"role": "user", "content": h[0]})
            messages.append({"role": "assistant", "content": h[1]})
        if system_msg != None:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": instruction})

    try:
        response = client.chat.completions.create(
            model               = MODEL,
            messages            = messages,
            stream              = stream,
            max_tokens          = max_tokens,
            frequency_penalty   = frequency_penalty,
            presence_penalty    = presence_penalty,
            stop                = stop_words,
            temperature         = temperature,
            top_p               = top_p,
            logprobs            = logprobs,
            top_logprobs        = top_logprobs
        )
        answer = response.choices[0].message.content
        return json.dumps(answer), 200
    except Exception as e:
        answer = "Error ! : " + str(e)
        logger.error(answer, exc_info=True)
        return json.dumps(answer), 500


# DO NOT REMOVE
@app.route('/healthz')
def liveness():
    # You can add custom logic here to check the application's liveness
    # For simplicity, we'll just return a 200 OK response.
    return json.dumps({'status': 'OK'})

# DO NOT REMOVE
# Health check endpoint for readiness probe
@app.route('/readyz')
def readiness():
    # You can add custom logic here to check the application's readiness
    # For simplicity, we'll just return a 200 OK response.
    return json.dumps({'status': 'OK'})
