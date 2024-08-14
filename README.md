# Liev Model Server - Deepseek Chat - Text
Liev Model Servers are meant to abstract prompt complexity in LLM Prompting.


```
                                ____________________________________
                                |                                  |
| The Liev Dispatcher |-------> | Liev Model Server Deepseek Chat  | -----> Deepseek AI API
                                |__________________________________|


```

## Installation

### Environment Variables

| Variable  | Description |Values | Default |
| ------------- |-------------|-------------|-------------|
| LOG_LEVEL     | Python logging level |CRITICAL, ERROR, WARNING, INFO, DEBUG      |INFO    |
| LIEV_USERNAME     | Username used for HTTP Basic Auth | User defined value | - |
| LIEV_PASSWORD     | Password user for HTTP Basic Auth     | User defined value | - |
| DEEPSEEKAPIKEY     | DeepSeek API Key    | User defined value - required  | - |
| BASE_URL     | Deepseek Base URL    | https://api.deepseek.com  | https://api.deepseek.com |
| MODEL     | Deepseek Model    | deepseek-chat or deepseek-coder(not recommended) | deepseek-chat |

# Running

#### Simple standalone - You may create a venv in you preferred way
```
$ pip install -r requirements.txt
$ start_model.sh
```

#### Docker - There is a Dockerfile for image building
```
$ docker build -t liev-deepseek-chat-model-server .
$ docker run -e <Envs> -d liev-deepseek-chat-model-server 
```

# Credits

- Adriano Lima and Cleber Marques (Inmetrics)
